import React from 'react';
import HeroSection from '../home/HeroSection';
import FeaturesSection from '../home/FeaturesSection';
import HowItWorks from '../home/HowItWorks';
import TrustScoreSection from '../home/TrustScoreSection';
import CTASection from '../home/CTASection';
import Navbar from '../common/Navbar';
import Footer from '../common/Footer';
import SectionNavigator from '../common/SectionNavigator';

function Home() {
  return (
    <div className="min-h-screen bg-black text-white">
      <Navbar />
      <div
        className="fixed inset-0 -z-10 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage:
            "url('https://raw.githubusercontent.com/prebuiltui/prebuiltui/refs/heads/main/assets/hero/bg-gradient-2.png')",
        }}
      />
      <main>
        <HeroSection />
        <FeaturesSection />
        <HowItWorks />
        <TrustScoreSection />
        <CTASection />
      </main>

      <SectionNavigator />
      <Footer />
    </div>
  );
}

export default Home;