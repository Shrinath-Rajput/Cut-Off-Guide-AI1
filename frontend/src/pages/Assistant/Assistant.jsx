import { useEffect, useRef, useState } from 'react';
import MainLayout from '../../components/MainLayout/MainLayout';
import './Assistant.css';

const suggestionButtons = [
  'What colleges can I get with my percentile?',
  'Which college is best for CSE?',
  'Compare these colleges',
];

const recentChats = [
  { id: 'top-engineering', title: 'Top Engineering Colleges in Maharashtra', selected: true },
  { id: 'cse-cutoffs', title: 'CSE Cutoffs for Tier 1', selected: false },
  { id: 'nit-compare', title: 'Comparing NIT Warangal & Trichy', selected: false },
];

const savedConversations = [
  { id: 'target-colleges', title: 'My Target Colleges List' },
];

const initialMessages = [
  {
    id: 'assistant-welcome',
    from: 'assistant',
    text: "Hello! I'm your Cutoff Guide AI. I can help you analyze admission chances, compare universities, or find the right course based on your scores. How can I assist you today?",
  },
  {
    id: 'user-sample',
    from: 'user',
    text: 'I scored 92 percentile in JEE Mains. Can I get Computer Science in any top NIT?',
  },
  {
    id: 'assistant-sample',
    from: 'assistant',
    text: 'With a 92 percentile in JEE Mains, securing Computer Science Engineering (CSE) in top-tier NITs (like Trichy, Warangal, or Surathkal) under the Open category will be highly challenging, as their cutoffs usually close above the 98-99 percentile mark.',
    details: 'However, you have good chances in:',
    list: [
      'Newer NITs (e.g., NIT Mizoram, NIT Nagaland) depending on your home state quota.',
      'Top state-level government colleges or reputed private institutions.',
      'Other branches like Civil or Metallurgical in mid-tier NITs.',
    ],
    action: 'Open Predictor with these stats',
  },
];

const Assistant = () => {
  const [messages, setMessages] = useState(initialMessages);
  const [query, setQuery] = useState('');
  const [activeChat, setActiveChat] = useState(recentChats[0].id);
  const [isTyping, setIsTyping] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chatHistoryRef = useRef(null);

  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const assistantApiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

  const sendAssistantMessage = async (messageText) => {
    const response = await fetch(`${assistantApiBase}/api/assistant`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: messageText }),
    });

    if (!response.ok) {
      throw new Error('Assistant backend request failed');
    }

    const data = await response.json();
    return data.reply || data.message || JSON.stringify(data);
  };

  const handleMessageSend = async (messageText) => {
    const text = messageText.trim();
    if (!text) return;

    const userMessage = {
      id: `user-${Date.now()}`,
      from: 'user',
      text,
    };

    setMessages((prev) => [...prev, userMessage]);
    setQuery('');
    setIsTyping(true);

    const pendingId = `assistant-pending-${Date.now()}`;
    setMessages((prev) => [...prev, { id: pendingId, from: 'assistant', pending: true }]);

    try {
      const assistantText = await sendAssistantMessage(text);
      setMessages((prev) => prev.map((message) => {
        if (message.id !== pendingId) return message;
        return { id: `assistant-${Date.now()}`, from: 'assistant', text: assistantText };
      }));
    } catch (error) {
      setMessages((prev) => prev.map((message) => {
        if (message.id !== pendingId) return message;
        return {
          id: `assistant-error-${Date.now()}`,
          from: 'assistant',
          text: 'Sorry, we could not reach the AI service right now. Please try again in a moment.',
          error: true,
        };
      }));
    } finally {
      setIsTyping(false);
    }
  };

  const handleSend = () => {
    handleMessageSend(query);
  };

  const handleSuggestion = (suggestion) => {
    handleMessageSend(suggestion);
  };

  const handleNewChat = () => {
    setMessages(initialMessages);
    setActiveChat(recentChats[0].id);
    setIsTyping(true);
    setSidebarOpen(false);
  };

  const handleSelectChat = (chatId) => {
    setActiveChat(chatId);
    setMessages(initialMessages);
    setSidebarOpen(false);
  };

  return (
    <MainLayout>
      <div className="assistant-page">
        <div className={`assistant-shell ${sidebarOpen ? 'sidebar-open' : ''}`}>
          <aside className="assistant-sidebar">
            <div className="sidebar-top">
              <button className="new-chat-button" type="button" onClick={handleNewChat}>
                <span className="material-symbols-outlined">add</span>
                New Chat
              </button>
            </div>

            <div className="sidebar-section">
              <div className="sidebar-heading">RECENT CHATS</div>
              <ul className="sidebar-list">
                {recentChats.map((chat) => (
                  <li
                    key={chat.id}
                    className={`sidebar-item ${activeChat === chat.id ? 'active' : ''}`}
                    onClick={() => handleSelectChat(chat.id)}
                  >
                    {chat.title}
                  </li>
                ))}
              </ul>
            </div>

            <div className="sidebar-section">
              <div className="sidebar-heading">SAVED CONVERSATIONS</div>
              <ul className="sidebar-list">
                {savedConversations.map((saved) => (
                  <li key={saved.id} className="sidebar-item saved-item">
                    <span>{saved.title}</span>
                    <span className="material-symbols-outlined bookmark-icon">bookmark</span>
                  </li>
                ))}
              </ul>
            </div>
          </aside>

          <section className="assistant-chat-area">
            <div className="chat-header-row">
              <button
                type="button"
                className="mobile-sidebar-toggle"
                onClick={() => setSidebarOpen(true)}
              >
                Chats
              </button>
            </div>

            <div className="chat-panel">
              <div className="chat-header">
                <div>
                  <h1>Your AI College Admission Assistant</h1>
                  <p>Ask anything about colleges, cutoffs, courses and admissions.</p>
                </div>
              </div>

              <div className="chat-history" ref={chatHistoryRef}>
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`chat-message ${message.from} ${message.pending ? 'pending' : ''} ${message.error ? 'error' : ''}`}
                  >
                    <div className="message-avatar">
                      <span className="material-symbols-outlined">
                        {message.from === 'assistant' ? 'smart_toy' : 'person'}
                      </span>
                    </div>
                    <div className="message-bubble">
                      <p>{message.text}</p>
                      {message.list && (
                        <ul className="assistant-list">
                          {message.list.map((item) => (
                            <li key={item}>{item}</li>
                          ))}
                        </ul>
                      )}
                      {message.action && (
                        <div className="recommendation-card">
                          <span className="recommendation-label">RECOMMENDED ACTION</span>
                          <div className="recommendation-content">
                            <span>{message.action}</span>
                            <span className="material-symbols-outlined">arrow_forward</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="chat-message assistant typing-row">
                    <div className="message-avatar">
                      <span className="material-symbols-outlined">smart_toy</span>
                    </div>
                    <div className="message-bubble typing-bubble">
                      <div className="typing-indicator">
                        <span />
                        <span />
                        <span />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="chat-input-shell">
                <div className="suggestion-chips">
                  {suggestionButtons.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      className="suggestion-chip"
                      onClick={() => handleSuggestion(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>

                <div className="chat-input-row">
                  <input
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="Type your academic query here..."
                    onKeyDown={(event) => {
                      if (event.key === 'Enter') {
                        event.preventDefault();
                        handleSend();
                      }
                    }}
                  />
                  <button type="button" className="send-button" onClick={handleSend}>
                    <span className="material-symbols-outlined">send</span>
                  </button>
                </div>
              </div>
            </div>
          </section>

          <div className="sidebar-backdrop" onClick={() => setSidebarOpen(false)} />
        </div>
      </div>
    </MainLayout>
  );
};

export default Assistant;
