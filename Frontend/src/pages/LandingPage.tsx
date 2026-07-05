import { Navbar } from '../components/layout/Navbar'
import { Footer } from '../components/layout/Footer'
import { ScrollStory } from '../components/landing/ScrollStory'
import { Benefits } from '../components/landing/sections/Benefits'
import { ContentTypes } from '../components/landing/sections/ContentTypes'
import { SampleInsights } from '../components/landing/sections/SampleInsights'
import { VsManual } from '../components/landing/sections/VsManual'
import { Reviews } from '../components/landing/sections/Reviews'
import { Faq } from '../components/landing/sections/Faq'

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main>
        <ScrollStory />
        <div id="benefits" className="scroll-mt-20"><Benefits /></div>
        <div id="content" className="scroll-mt-20"><ContentTypes /></div>
        <div id="sample" className="scroll-mt-20"><SampleInsights /></div>
        <VsManual />
        <div id="reviews" className="scroll-mt-20"><Reviews /></div>
        <div id="faq" className="scroll-mt-20"><Faq /></div>
      </main>
      <Footer />
    </div>
  )
}
