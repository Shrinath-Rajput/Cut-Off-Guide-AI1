import { useEffect, useRef, useState } from 'react';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import './Assistant.css';

const DEFAULT_SUGGESTIONS = [
  'What colleges can I get with my percentile?',
  'Which college is best for CSE in Maharashtra?',
  'Compare COEP vs VJTI for Computer Engineering',
  'What are the cutoffs for Tier 1 NITs?',
];

const DEFAULT_WELCOME_MESSAGE = {
  id: 'welcome-msg',
  from: 'assistant',
  text: "Hello! I'm your CutoffGuide AI Council. I can help you analyze admission chances, compare colleges, check cutoffs, and navigate the counseling process. How can I assist you today?",
  timestamp: Date.now(),
};

const STORAGE_KEY = 'cutoffguide_ai_chats';

const loadSavedChats = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed;
      }
    }
  } catch (err) {
    console.error('Failed to load chat history from localStorage', err);
  }

  // Initial seed chat if empty
  const defaultChat = {
    id: `chat-${Date.now()}`,
    title: 'Top Engineering Colleges in Maharashtra',
    createdAt: Date.now(),
    messages: [
      DEFAULT_WELCOME_MESSAGE,
      {
        id: 'seed-user',
        from: 'user',
        text: 'I scored 92 percentile in JEE Mains. Can I get Computer Science in any top NIT?',
        timestamp: Date.now() - 60000,
      },
      {
        id: 'seed-assistant',
        from: 'assistant',
        text: 'With a 92 percentile in JEE Mains, your approximate general rank is around 80,000 to 90,000.\n\nSecuring Computer Science Engineering (CSE) in top-tier NITs (like Trichy, Warangal, or Surathkal) under the Open category will be highly challenging, as their cutoffs usually close within the top 5,000 ranks.',
        listTitle: 'Alternative Options to Consider:',
        list: [
          'Newer NITs (e.g., NIT Mizoram, NIT Nagaland, NIT Sikkim) during CSAB special rounds.',
          'Top state-level government colleges or reputed autonomous institutions where home state quota applies.',
          'Other high-demand branches like ECE, IT, or Electrical in mid-tier NITs.',
        ],
        suggestions: [
          'Yes, show me target colleges',
          'What about ECE in top colleges?',
        ],
        timestamp: Date.now() - 30000,
      },
    ],
  };

  return [defaultChat];
};

const Assistant = () => {
  const [chats, setChats] = useState(loadSavedChats);
  const [activeChatId, setActiveChatId] = useState(() => {
    const loaded = loadSavedChats();
    return loaded[0]?.id || `chat-${Date.now()}`;
  });
  const [query, setQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const chatHistoryRef = useRef(null);
  const textareaRef = useRef(null);

  // Save chats to localStorage whenever chats state changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(chats));
    } catch (err) {
      console.error('Failed to save chat history to localStorage', err);
    }
  }, [chats]);

  const currentChat = chats.find((c) => c.id === activeChatId) || chats[0];
  const messages = currentChat?.messages || [DEFAULT_WELCOME_MESSAGE];

  // Scroll to bottom on new message or typing
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 128)}px`;
    }
  }, [query]);

  const assistantApiBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000';

  const handleNewChat = () => {
    const newChatId = `chat-${Date.now()}`;
    const newChat = {
      id: newChatId,
      title: 'New Conversation',
      createdAt: Date.now(),
      messages: [
        {
          ...DEFAULT_WELCOME_MESSAGE,
          id: `welcome-${Date.now()}`,
          timestamp: Date.now(),
        },
      ],
    };

    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(newChatId);
    setSidebarOpen(false);
    if (textareaRef.current) textareaRef.current.focus();
  };

  const handleSelectChat = (chatId) => {
    setActiveChatId(chatId);
    setSidebarOpen(false);
  };

  const handleDeleteChat = (e, chatId) => {
    e.stopPropagation();
    setChats((prev) => {
      const filtered = prev.filter((c) => c.id !== chatId);
      if (filtered.length === 0) {
        const fresh = {
          id: `chat-${Date.now()}`,
          title: 'New Conversation',
          createdAt: Date.now(),
          messages: [{ ...DEFAULT_WELCOME_MESSAGE, id: `welcome-${Date.now()}`, timestamp: Date.now() }],
        };
        setActiveChatId(fresh.id);
        return [fresh];
      }
      if (activeChatId === chatId) {
        setActiveChatId(filtered[0].id);
      }
      return filtered;
    });
  };

  const parseMessageDetails = (rawText) => {
    let cleanText = rawText || '';
    // Strip <think>...</think> if returned by deepseek models
    cleanText = cleanText.replace(/<think>[\s\S]*?<\/think>/g, '').trim();

    return {
      text: cleanText,
    };
  };

  const handleMessageSend = async (messageText) => {
    const text = messageText.trim();
    if (!text || isTyping) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      from: 'user',
      text,
      timestamp: Date.now(),
    };

    // Update active chat title if it's the first user message
    const isFirstUserMessage = messages.filter((m) => m.from === 'user').length === 0;
    const updatedTitle = isFirstUserMessage
      ? text.length > 40
        ? `${text.slice(0, 40)}...`
        : text
      : currentChat.title;

    // Append user message immediately
    setChats((prev) =>
      prev.map((chat) => {
        if (chat.id !== activeChatId) return chat;
        return {
          ...chat,
          title: updatedTitle,
          messages: [...chat.messages, userMessage],
        };
      })
    );

    setQuery('');
    if (textareaRef.current) {
      textareaRef.current.style.height = '52px';
    }
    setIsTyping(true);

    // Build context history for LLM
    const historyPayload = messages
      .filter((m) => !m.pending && !m.error)
      .map((m) => ({
        role: m.from === 'user' ? 'user' : 'assistant',
        content: m.text || '',
      }));

    try {
      const data = await sendAssistantChat(text, historyPayload);
      const replyRaw = data.reply || data.message || 'No response received.';
      const parsed = parseMessageDetails(replyRaw);

      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        from: 'assistant',
        text: parsed.text,
        timestamp: Date.now(),
      };

      setChats((prev) =>
        prev.map((chat) => {
          if (chat.id !== activeChatId) return chat;
          return {
            ...chat,
            messages: [...chat.messages, assistantMessage],
          };
        })
      );
    } catch (error) {
      console.error('Assistant chat error', error);
      const errorMessage = {
        id: `assistant-error-${Date.now()}`,
        from: 'assistant',
        text: 'Sorry, we encountered an issue communicating with the AI service. Please check that the server and Hugging Face configuration are active.',
        error: true,
        timestamp: Date.now(),
      };

      setChats((prev) =>
        prev.map((chat) => {
          if (chat.id !== activeChatId) return chat;
          return {
            ...chat,
            messages: [...chat.messages, errorMessage],
          };
        })
      );
    } finally {
      setIsTyping(false);
    }
  };

  const handleSend = () => {
    handleMessageSend(query);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="assistant-page-shell">
      <Navbar />

      <div className="assistant-content-wrapper">
        <div className={`assistant-layout ${sidebarOpen ? 'sidebar-open' : ''}`}>
          {/* Side Navigation Bar */}
          <nav className="assistant-sidenav">
            {/* Header */}
            <div className="sidenav-header">
              <div className="sidenav-logo-badge">
                <span className="material-symbols-outlined text-[24px]">school</span>
              </div>
              <div className="sidenav-brand-text">
                <h2 className="sidenav-title">AI Council</h2>
                <p className="sidenav-subtitle">Your Academic Guide</p>
              </div>
            </div>

            {/* CTA: New Chat */}
            <button className="sidenav-new-chat-btn" type="button" onClick={handleNewChat}>
              <span className="material-symbols-outlined text-sm">add</span>
              New Chat
            </button>

            {/* Navigation Tabs / Recent Chats */}
            <div className="sidenav-scroll-area chat-scroll">
              <div className="sidenav-section">
                <div className="sidenav-section-header">
                  <span className="material-symbols-outlined text-[18px]">chat_bubble</span>
                  <h3>Recent Chats</h3>
                </div>
                <ul className="sidenav-chat-list">
                  {chats.map((chat) => (
                    <li key={chat.id}>
                      <button
                        type="button"
                        className={`sidenav-chat-item ${activeChatId === chat.id ? 'active' : ''}`}
                        onClick={() => handleSelectChat(chat.id)}
                      >
                        <span className="truncate flex-1 text-left">{chat.title || 'Untitled Conversation'}</span>
                        <span
                          className="material-symbols-outlined chat-delete-btn"
                          onClick={(e) => handleDeleteChat(e, chat.id)}
                          title="Delete chat"
                        >
                          close
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Footer note */}
            <div className="sidenav-footer">
              <p className="text-xs text-on-surface-variant/60">Powered by Llama-3.1-8B Instruct</p>
            </div>
          </nav>

          {/* Main Content Area */}
          <main className="assistant-main-panel">
            {/* Subtle Radial Background Pattern */}
            <div className="assistant-bg-pattern" />

            {/* Mobile Sidebar Trigger (Compact float) */}
            <div className="md:hidden flex items-center justify-between px-4 py-2 border-b border-outline-variant/40 bg-surface/80">
              <button
                className="flex items-center gap-1.5 text-xs font-bold text-primary bg-primary-fixed py-1.5 px-3 rounded-lg border border-primary-fixed"
                type="button"
                onClick={() => setSidebarOpen(true)}
              >
                <span className="material-symbols-outlined text-sm">menu</span>
                <span>Chat History</span>
              </button>
              <button
                className="flex items-center gap-1 text-xs font-bold text-on-surface bg-surface-container-high py-1.5 px-3 rounded-lg border border-outline-variant"
                type="button"
                onClick={handleNewChat}
              >
                <span className="material-symbols-outlined text-sm">add</span>
                <span>New Chat</span>
              </button>
            </div>

            {/* Chat Interface Scroll Area */}
            <div className="chat-messages-container chat-scroll" ref={chatHistoryRef}>
              <div className="messages-inner-wrap">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`message-row ${message.from === 'user' ? 'user-row' : 'assistant-row'} ${
                      message.error ? 'error-row' : ''
                    }`}
                  >
                    <div className={`avatar-box ${message.from === 'user' ? 'user-avatar' : 'assistant-avatar'}`}>
                      <span className="material-symbols-outlined text-[18px]">
                        {message.from === 'user' ? 'person' : 'school'}
                      </span>
                    </div>

                    <div className={`message-bubble-box ${message.from === 'user' ? 'user-bubble' : 'assistant-bubble'}`}>
                      <div className="bubble-content">
                        <p className="bubble-text">{message.text}</p>

                        {message.list && message.list.length > 0 && (
                          <div className="bubble-callout-card">
                            {message.listTitle && (
                              <h4 className="callout-title">
                                <span className="material-symbols-outlined text-[18px]">analytics</span>
                                {message.listTitle}
                              </h4>
                            )}
                            <ul className="callout-list">
                              {message.list.map((item, idx) => (
                                <li key={idx}>{item}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {message.suggestions && message.suggestions.length > 0 && (
                          <div className="message-suggestions-row">
                            {message.suggestions.map((sug, idx) => (
                              <button
                                key={idx}
                                type="button"
                                className="suggestion-action-btn"
                                onClick={() => handleMessageSend(sug)}
                              >
                                {sug}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* Typing indicator */}
                {isTyping && (
                  <div className="message-row assistant-row typing-row">
                    <div className="avatar-box assistant-avatar">
                      <span className="material-symbols-outlined text-[18px]">school</span>
                    </div>
                    <div className="message-bubble-box assistant-bubble typing-bubble">
                      <div className="typing-dots">
                        <span />
                        <span />
                        <span />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Fixed Bottom Input Area */}
            <div className="chat-input-bottom-bar">
              <div className="input-inner-container">
                {/* Quick Suggestion Chips */}
                <div className="quick-suggestions-chips">
                  {DEFAULT_SUGGESTIONS.map((sug, idx) => (
                    <button
                      key={idx}
                      type="button"
                      className="chip-btn"
                      onClick={() => handleMessageSend(sug)}
                    >
                      {sug}
                    </button>
                  ))}
                </div>

                {/* Input Box */}
                <div className="input-glass-box">
                  <button type="button" className="input-action-btn" aria-label="Attachment">
                    <span className="material-symbols-outlined">attach_file</span>
                  </button>
                  <textarea
                    ref={textareaRef}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask your admissions or cutoff question..."
                    rows={1}
                    className="chat-textarea"
                  />
                  <button
                    type="button"
                    className="input-send-btn"
                    onClick={handleSend}
                    disabled={!query.trim() || isTyping}
                    aria-label="Send message"
                  >
                    <span className="material-symbols-outlined text-[20px]">send</span>
                  </button>
                </div>

                <div className="disclaimer-text">
                  <p>AI can make mistakes. Always verify cutoffs with official JoSAA / CSAB / CET Cell counseling data.</p>
                </div>
              </div>
            </div>

            {/* Mobile backdrop */}
            <div className="mobile-backdrop" onClick={() => setSidebarOpen(false)} />
          </main>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default Assistant;
