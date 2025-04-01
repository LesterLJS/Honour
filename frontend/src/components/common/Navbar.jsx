import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <Link to="/upload" className="navbar-brand">
        Image Verification System
      </Link>
      
      <ul className="navbar-nav">
        
        <li className="nav-item">
          <Link to="/upload" className="nav-link">Upload</Link>
        </li>
        
       
        
        {isAdmin() && (
          <li className="nav-item">
            <Link to="/admin" className="nav-link">Admin</Link>
          </li>
        )}
        
        <li className="nav-item">
          <button 
            onClick={handleLogout} 
            className="nav-link" 
            style={{ background: 'none', border: 'none', cursor: 'pointer' }}
          >
            Logout
          </button>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;
