import { useState } from 'react'
import './App.css'
import Nav from './components/NAV/Nav'
import '../node_modules/bootstrap/dist/css/bootstrap.min.css'
import '../node_modules/bootstrap/dist/js/bootstrap.bundle.min.js'
import { BrowserRouter } from 'react-router-dom'
import Footer from './components/FOOTER/Footer.jsx'

function App() {


  return (
   <>
     <Nav/>
     <Footer />
   </>
  )
}

export default App
