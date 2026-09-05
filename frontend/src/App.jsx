import React from "react";

import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import DesignGallery from "./components/DesignGallery";
import Footer from "./components/Footer";
import designsData from "./data/designsData";

import "./App.css";

function App() {
  return (
    <div className="app">
      <Navbar />

      <main>
        <Hero />
        <DesignGallery designs={designsData} />
      </main>

      <Footer />
    </div>
  );
}

export default App;
