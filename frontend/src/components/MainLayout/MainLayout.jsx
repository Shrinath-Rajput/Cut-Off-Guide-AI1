import Footer from '../Footer/Footer';
import Navbar from '../Navbar/Navbar';
import './MainLayout.css';

const MainLayout = ({ children }) => {
  return (
    <div className="layout-shell">
      <Navbar />
      <main className="layout-content">{children}</main>
      <Footer />
    </div>
  );
};

export default MainLayout;
