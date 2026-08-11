import React from 'react';
import HeroSection from '../home/HeroSection';
import FeaturesSection from '../home/FeaturesSection';
import HowItWorks from '../home/HowItWorks';
import TrustScoreSection from '../home/TrustScoreSection';
import CTASection from '../home/CTASection';

function Home() {
  return (
    <main className="min-h-screen bg-black text-white">
      <HeroSection />
      <FeaturesSection />
      <HowItWorks />
      <TrustScoreSection />
      <CTASection />
    </main>
  );
}

export default Home;