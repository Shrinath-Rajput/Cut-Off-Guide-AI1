import { useCallback, useEffect, useState } from 'react';
import { ArrowLeft, BarChart3, Database, Image, LayoutDashboard, LogOut, Menu, MessageSquare, Pencil, Plus, Search, ShieldCheck, Trash2, Users, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  createAdminCollege, createAdminCutoff, createAdminSubscription, deleteAdminCollege, deleteAdminCutoff, deleteAdminEnquiry, deleteAdminImage, deleteAdminSubscription, deleteAdminUser,
  getAdminColleges, getAdminDashboard, getAdminCutoffs, getAdminEnquiries, getAdminImages, getAdminSubscriptions, getAdminUsers, replaceAdminImage, trainAdminDatabase, updateAdminCollege, updateAdminCutoff, updateAdminEnquiry, updateAdminImage, updateAdminSubscription, updateAdminUser, uploadAdminImage,
} from '../../services/api';
import './AdminPanel.css';

const modules = [
  ['dashboard', 'Dashboard', LayoutDashboard], ['users', 'Manage Users', Users], ['enquiries', 'Enquiries', MessageSquare], ['data', 'Manage Data', Database], ['images', 'UI Images', Image], ['plans', 'Subscription Plans', BarChart3],
];
const superAdminModules = [
  ['dashboard', 'Dashboard', LayoutDashboard], ['admin-panel', 'Admin Panel', ShieldCheck], ['users', 'Manage Users', Users], ['data', 'Manage Data', Database],
];
const emptyCollege = { name: '', rank: '', location: '', state: '', type: 'Private', rating: '', courses: '', feeLabel: '', feeValue: '', cutoff: '' };
const emptyCutoff = { college_name: '', course: '', category: '', gender: '', university: '', location: '', round: '', percentile: '', rank: '' };
const emptyPlan = { name: '', price: '', duration: '', features: '', limits: '' };
const date = (value) => value ? new Date(value).toLocaleDateString() : '—';
const errorText = (error) => error.response?.data?.detail || 'Something went wrong';

const AdminPanel = ({ section: initialSection = 'dashboard' }) => {
  const { adminUser, adminLogout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const isSuperAdminRoute = location.pathname.startsWith('/super-admin/');
  const routeSection = location.pathname.split('/')[2] || initialSection;
  const superAdminActiveKey = location.pathname.startsWith('/super-admin/admin-panel') ? 'admin-panel' : location.pathname.startsWith('/super-admin/users') ? 'users' : location.pathname.startsWith('/super-admin/data') ? 'data' : 'dashboard';
  const section = isSuperAdminRoute ? (
    location.pathname.startsWith('/super-admin/admin-panel') ? 'dashboard' :
    location.pathname.startsWith('/super-admin/users') ? 'users' :
    location.pathname.startsWith('/super-admin/data') ? 'data' :
    'dashboard'
  ) : routeSection === 'subscriptions' ? 'plans' : routeSection;
  const sidebarModules = isSuperAdminRoute ? superAdminModules : modules;
  const [mobileOpen, setMobileOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({ dashboard: null, users: [], colleges: [], cutoffs: [], enquiries: [], plans: [], images: [] });
  const [search, setSearch] = useState('');
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState({});

  const refresh = useCallback(async (target = section) => {
    setLoading(true);
    try {
      if (target === 'dashboard') { const result = await getAdminDashboard(); setData((current) => ({ ...current, dashboard: result.data })); }
      if (target === 'users') { const result = await getAdminUsers({ search }); setData((current) => ({ ...current, users: result.data || [] })); }
      if (target === 'data') { const [colleges, cutoffs] = await Promise.all([getAdminColleges(), getAdminCutoffs({ search })]); setData((current) => ({ ...current, colleges: colleges.data || [], cutoffs: cutoffs.data || [] })); }
      if (target === 'enquiries') { const result = await getAdminEnquiries({ search }); setData((current) => ({ ...current, enquiries: result.data || [] })); }
      if (target === 'plans') { const result = await getAdminSubscriptions(); setData((current) => ({ ...current, plans: result.data || [] })); }
      if (target === 'images') { const result = await getAdminImages(); setData((current) => ({ ...current, images: result.data || [] })); }
    } catch (error) { toast.error(errorText(error)); }
    finally { setLoading(false); }
  }, [search, section]);

  useEffect(() => { const timer = setTimeout(() => refresh(section), 0); return () => clearTimeout(timer); }, [refresh, section]);
  const open = (type, item = {}) => { setModal(type); setForm(item); };
  const close = () => { setModal(null); setForm({}); };
  const field = (name, value) => setForm((current) => ({ ...current, [name]: value }));
  const destroy = async (label, action) => { if (!window.confirm(`Delete this ${label}? This cannot be undone.`)) return; try { await action(); toast.success(`${label} deleted`); refresh(); } catch (error) { toast.error(errorText(error)); } };
  const save = async (type) => {
    try {
      if (type === 'college') { const payload = { ...form, rank: Number(form.rank), feeValue: Number(form.feeValue), courses: typeof form.courses === 'string' ? form.courses.split(',').map((item) => item.trim()).filter(Boolean) : form.courses }; form.id ? await updateAdminCollege(form.id, payload) : await createAdminCollege(payload); }
      if (type === 'cutoff') form.id ? await updateAdminCutoff(form.id, form) : await createAdminCutoff(form);
      if (type === 'plan') { const payload = { ...form, price: Number(form.price), features: typeof form.features === 'string' ? form.features.split(',').map((item) => item.trim()).filter(Boolean) : form.features }; form.id ? await updateAdminSubscription(form.id, payload) : await createAdminSubscription(payload); }
      close(); toast.success('Changes saved'); refresh();
    } catch (error) { toast.error(errorText(error)); }
  };
  const signOut = () => { adminLogout(); navigate('/login', { replace: true }); };

  return <div className="admin-app">
    <aside className={`admin-sidebar ${mobileOpen ? 'open' : ''}`}>
      <div className="admin-brand">
        <div className="admin-brand-shell">
          <span className="admin-brand-mark" aria-hidden="true">
            <img src="/favicon.svg" alt="FOURISE" />
          </span>
          <div className="admin-brand-copy">
            <span className="admin-brand-name">Cutoff Guide <b>AI</b></span>
            <small className="admin-brand-company">FOURISE</small>
          </div>
        </div>
        <button className="admin-close" onClick={() => setMobileOpen(false)}><X size={18} /></button>
      </div>
      <nav>{sidebarModules.map(([id, label, Icon]) => <button className={(isSuperAdminRoute ? superAdminActiveKey : section) === id ? 'active' : ''} key={id} onClick={() => {
        const target = isSuperAdminRoute ? (
          id === 'dashboard' ? '/super-admin/dashboard' :
          id === 'users' ? '/super-admin/users' :
          id === 'data' ? '/super-admin/data' :
          '/super-admin/admin-panel'
        ) : `/admin/${id === 'plans' ? 'subscriptions' : id}`;
        navigate(target);
        setMobileOpen(false);
      }}><Icon size={18} />{label}</button>)}</nav>
      <button className="admin-logout" onClick={signOut}><LogOut size={18} />Logout</button>
    </aside>
    {mobileOpen && <button className="admin-overlay" aria-label="Close menu" onClick={() => setMobileOpen(false)} />}
    <main className="admin-main">
      <header className="admin-topbar"><button className="admin-menu" onClick={() => setMobileOpen(true)}><Menu size={21} /></button><div><p className="admin-kicker">{isSuperAdminRoute ? 'SUPER ADMIN' : 'ADMIN PANEL'}</p><h1>{(isSuperAdminRoute ? sidebarModules : modules).find(([id]) => id === (isSuperAdminRoute ? superAdminActiveKey : section))?.[1] || 'Dashboard'}</h1></div><div className="admin-user"><span>{adminUser?.name?.slice(0, 1) || 'A'}</span><div><strong>{adminUser?.name || 'Administrator'}</strong><small>{adminUser?.email || 'Admin account'}</small></div></div></header>
      <div className="admin-content">{loading && <div className="admin-loading">Loading workspace...</div>}{!loading && section === 'dashboard' && <Dashboard data={data.dashboard} onTrain={async () => { const result = await trainAdminDatabase(); toast(result.message); }} />}{!loading && section === 'users' && <UsersView items={data.users} search={search} setSearch={setSearch} reload={() => refresh('users')} onEdit={(item) => open('user', item)} onDelete={(id) => destroy('user', () => deleteAdminUser(id))} />}{!loading && section === 'enquiries' && <EnquiriesView items={data.enquiries} search={search} setSearch={setSearch} onDelete={(id) => destroy('enquiry', () => deleteAdminEnquiry(id))} onUpdate={async (id, payload) => { await updateAdminEnquiry(id, payload); toast.success('Enquiry updated'); refresh(); }} />}{!loading && section === 'data' && <DataView colleges={data.colleges} cutoffs={data.cutoffs} search={search} setSearch={setSearch} onAddCollege={() => open('college', emptyCollege)} onEditCollege={(item) => open('college', { ...item, courses: item.courses?.join(', ') })} onDeleteCollege={(id) => destroy('college', () => deleteAdminCollege(id))} onAddCutoff={() => open('cutoff', emptyCutoff)} onEditCutoff={(item) => open('cutoff', item)} onDeleteCutoff={(id) => destroy('cutoff', () => deleteAdminCutoff(id))} />}{!loading && section === 'plans' && <PlansView items={data.plans} onAdd={() => open('plan', emptyPlan)} onEdit={(item) => open('plan', { ...item, features: item.features?.join(', ') })} onToggle={async (id, isActive) => { await updateAdminSubscription(id, { isActive }); toast.success('Plan updated'); refresh('plans'); }} onDelete={(id) => destroy('plan', () => deleteAdminSubscription(id))} />}{!loading && section === 'images' && <ImagesView items={data.images} onUpload={async (file, imageSection, name) => { await uploadAdminImage(file, imageSection, name); toast.success('Image uploaded'); refresh('images'); }} onReplace={async (id, file) => { await replaceAdminImage(id, file); toast.success('Image replaced'); refresh('images'); }} onToggle={async (id, isActive) => { await updateAdminImage(id, { isActive }); refresh('images'); }} onDelete={(id) => destroy('image', () => deleteAdminImage(id))} />}</div>
    </main>
    {modal && <Modal title={`${form.id ? 'Edit' : 'Add'} ${modal}`} onClose={close}>{modal === 'user' && <UserForm form={form} field={field} onSave={async () => { await updateAdminUser(form.id, form); close(); toast.success('User updated'); refresh(); }} onBack={close} />}{modal === 'college' && <RecordForm form={form} field={field} fields={Object.keys(emptyCollege)} onSave={() => save('college')} onBack={close} />}{modal === 'cutoff' && <RecordForm form={form} field={field} fields={Object.keys(emptyCutoff)} onSave={() => save('cutoff')} onBack={close} />}{modal === 'plan' && <RecordForm form={form} field={field} fields={Object.keys(emptyPlan)} onSave={() => save('plan')} onBack={close} />}</Modal>}
  </div>;
};

const Dashboard = ({ data, onTrain }) => <><section className="admin-welcome"><div><p className="admin-kicker">OVERVIEW</p><p>Monitor the people, data, and content powering Cutoff Guide AI.</p></div><button className="admin-secondary-button" onClick={onTrain}><Database size={16} />Update database</button></section><section className="stat-grid">{[['Total Users', data?.totalUsers], ['Active Users', data?.activeUsers], ['Total Enquiries', data?.totalEnquiries], ['Total Colleges', data?.totalColleges], ['Total Cutoff Records', data?.totalCutoffs], ['Active Subscription Plans', data?.activePlans]].map(([label, value]) => <article className="stat-card" key={label}><span>{label}</span><strong>{value ?? 0}</strong><small>Live from database</small></article>)}</section><section className="admin-two-column"><Panel title="Recent users"><SimpleList items={data?.recentUsers} empty="No users yet" primary="name" secondary="email" /></Panel><Panel title="Recent enquiries"><SimpleList items={data?.recentEnquiries} empty="No enquiries yet" primary="subject" secondary="status" /></Panel></section></>;
const Panel = ({ title, children, action }) => <section className="admin-panel"><div className="panel-heading"><h3>{title}</h3>{action}</div>{children}</section>;
const SimpleList = ({ items = [], empty, primary, secondary }) => items.length ? <div className="simple-list">{items.map((item) => <div className="simple-row" key={item.id}><div><strong>{item[primary] || 'Untitled'}</strong><small>{item[secondary] || '—'}</small></div><time>{date(item.createdAt)}</time></div>)}</div> : <p className="empty-state">{empty}</p>;
const Toolbar = ({ search, setSearch, children }) => <div className="admin-toolbar"><label className="search-box"><Search size={17} /><input placeholder="Search records" value={search} onChange={(event) => setSearch(event.target.value)} /></label>{children}</div>;
const Actions = ({ onEdit, onDelete }) => <div className="row-actions">{onEdit && <button className="admin-icon-button" title="Edit" onClick={onEdit}><Pencil size={16} /></button>}{onDelete && <button className="admin-icon-button admin-icon-button-danger" title="Delete" onClick={onDelete}><Trash2 size={16} /></button>}</div>;
const UsersView = ({ items, search, setSearch, onEdit, onDelete }) => <><Toolbar search={search} setSearch={setSearch} /><Panel title={`${items.length} users`}><Table headers={['Name', 'Contact', 'Status', 'Joined', '']} rows={items.map((item) => [<strong>{item.name || 'Unnamed'}</strong>, <span>{item.email || item.phone || '—'}</span>, <span className={`status ${item.isActive === false ? 'off' : ''}`}>{item.isActive === false ? 'Inactive' : 'Active'}</span>, date(item.createdAt), <Actions onEdit={() => onEdit(item)} onDelete={() => onDelete(item.id)} />])} empty="No users match this search." /></Panel></>;
const EnquiriesView = ({ items, search, setSearch, onDelete, onUpdate }) => <><Toolbar search={search} setSearch={setSearch} /><Panel title={`${items.length} enquiries`}><Table headers={['Enquiry', 'User', 'Status', 'Received', 'Actions']} rows={items.map((item) => [<div><strong>{item.subject || 'General enquiry'}</strong><small>{item.message?.slice(0, 70) || 'No message'}</small></div>, item.email || item.name || '—', <select className="table-select" value={item.status || 'Pending'} onChange={(event) => onUpdate(item.id, { status: event.target.value })}><option>Pending</option><option>In Progress</option><option>Resolved</option></select>, date(item.createdAt), <Actions onDelete={() => onDelete(item.id)} />])} empty="No enquiries yet." /></Panel></>;
const DataView = ({ colleges, cutoffs, search, setSearch, onAddCollege, onEditCollege, onDeleteCollege, onAddCutoff, onEditCutoff, onDeleteCutoff }) => <><Toolbar search={search} setSearch={setSearch}><button className="admin-primary-button" onClick={onAddCollege}><Plus size={16} />College</button><button className="admin-secondary-button" onClick={onAddCutoff}><Plus size={16} />Cutoff</button></Toolbar><Panel title={`${colleges.length} colleges`}><Table headers={['College', 'Location', 'Type', 'Rank', '']} rows={colleges.map((item) => [<strong>{item.name}</strong>, item.location || item.state || '—', item.type || '—', item.rank || '—', <Actions onEdit={() => onEditCollege(item)} onDelete={() => onDeleteCollege(item.id)} />])} empty="No colleges found." /></Panel><Panel title={`${cutoffs.length} cutoff records`}><Table headers={['College', 'Course', 'Category', 'Percentile', '']} rows={cutoffs.map((item) => [item.college_name || '—', item.course || '—', item.category || '—', item.percentile || '—', <Actions onEdit={() => onEditCutoff(item)} onDelete={() => onDeleteCutoff(item.id)} />])} empty="No cutoff records found." /></Panel></>;
const PlansView = ({ items, onAdd, onEdit, onToggle, onDelete }) => <><div className="section-heading"><div><p className="admin-kicker">REVENUE</p><h2>Plans that fit every learner</h2></div><button className="admin-primary-button" onClick={onAdd}><Plus size={16} />Add plan</button></div><section className="plan-grid">{items.map((item) => <article className="plan-card" key={item.id}><div><span className={`status ${item.isActive === false ? 'off' : ''}`}>{item.isActive === false ? 'Inactive' : 'Active'}</span><h3>{item.name}</h3><strong>{item.price || 0}</strong><small>{item.duration || 'Flexible duration'}</small></div><ul>{(item.features || []).map((feature) => <li key={feature}>{feature}</li>)}</ul><div className="plan-actions"><button className="admin-card-button" onClick={() => onToggle(item.id, item.isActive === false)}>{item.isActive === false ? 'Activate' : 'Deactivate'}</button><button className="admin-card-button admin-card-button-secondary" onClick={() => onEdit(item)}><Pencil size={15} />Edit</button><button className="admin-card-button admin-card-button-danger" onClick={() => onDelete(item.id)}><Trash2 size={15} />Delete</button></div></article>)}</section>{!items.length && <p className="empty-state">No plans configured.</p>}</>;
const ImagesView = ({ items, onUpload, onReplace, onToggle, onDelete }) => { const [section, setSection] = useState('Home Hero'); const [name, setName] = useState(''); return <><div className="section-heading"><div><p className="admin-kicker">CONTENT LIBRARY</p><h2>Images across the guide</h2></div><label className="admin-primary-button"><Plus size={16} />Upload image<input hidden type="file" accept="image/*" onChange={(event) => { if (event.target.files?.[0]) onUpload(event.target.files[0], section, name); }} /></label></div><div className="image-controls"><input placeholder="Image name" value={name} onChange={(event) => setName(event.target.value)} /><select value={section} onChange={(event) => setSection(event.target.value)}><option>Home Hero</option><option>College sections</option><option>Promotional banners</option><option>Other homepage UI images</option></select></div><section className="image-grid">{items.map((item) => <article className="managed-image" key={item.id}><img src={item.url} alt={item.name} /><div><span className="image-section">{item.section}</span><h3>{item.name}</h3><small>Updated {date(item.updatedAt)}</small><div className="plan-actions"><button className="admin-card-button" onClick={() => onToggle(item.id, !item.isActive)}>{item.isActive === false ? 'Enable' : 'Disable'}</button><label className="replace-image admin-inline-button">Replace<input hidden type="file" accept="image/*" onChange={(event) => { if (event.target.files?.[0]) onReplace(item.id, event.target.files[0]); }} /></label><button className="admin-card-button admin-card-button-danger" onClick={() => onDelete(item.id)}><Trash2 size={15} />Delete</button></div></div></article>)}</section>{!items.length && <p className="empty-state">No managed UI images yet.</p>}</>; };
const UserForm = ({ form, field, onSave }) => <form className="admin-form" onSubmit={(event) => { event.preventDefault(); onSave(); }}><label>Name<input required value={form.name || ''} onChange={(event) => field('name', event.target.value)} /></label><label>Email<input type="email" value={form.email || ''} onChange={(event) => field('email', event.target.value)} /></label><label>Phone<input value={form.phone || ''} onChange={(event) => field('phone', event.target.value)} /></label><label className="check-row"><input type="checkbox" checked={form.isActive !== false} onChange={(event) => field('isActive', event.target.checked)} /> Account active</label><div className="admin-form-actions"><button className="admin-primary-button">Save user</button></div></form>;
const RecordForm = ({ form, field, fields, onSave }) => <form className="admin-form modal-form" onSubmit={(event) => { event.preventDefault(); onSave(); }}>{fields.map((name) => <label key={name}>{name.replaceAll('_', ' ')}<input required={!['rating', 'feeLabel', 'cutoff', 'limits'].includes(name)} value={form[name] ?? ''} onChange={(event) => field(name, event.target.value)} /></label>)}<div className="admin-form-actions"><button className="admin-primary-button">Save changes</button></div></form>;
const Modal = ({ title, onClose, children }) => <div className="modal-backdrop"><section className="admin-modal"><div className="panel-heading"><div className="admin-modal-header-actions"><button className="admin-secondary-button admin-back-button" onClick={onClose}><ArrowLeft size={15} />Back</button></div><h2>{title}</h2></div>{children}</section></div>;
const Table = ({ headers, rows, empty }) => rows.length ? <div className="table-wrap"><table><thead><tr>{headers.map((header) => <th key={header}>{header}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={index}>{row.map((cell, cellIndex) => <td key={cellIndex}>{cell}</td>)}</tr>)}</tbody></table></div> : <p className="empty-state">{empty}</p>;

export default AdminPanel;
