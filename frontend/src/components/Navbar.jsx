import React from 'react';
import './Navbar.css';

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-brand">Mousum Graphics</div>
      <ul className="nav-links">
        <li><a href="#home">Home</a></li>
        <li><a href="#gallery">Gallery</a></li>
        <li><a href="#footer">Contact</a></li>
      </ul>
    </nav>
  );
}
