import React, { useEffect } from 'react';
import homeimg  from '../../assets/dynavac.png';
import './Home.css';
import SplitText from "./Splitetext.jsx";


const handleAnimationComplete = () => {
  console.log('All letters have animated!');
};



const Home = () => {
  return (
    <>
    <section>

      <div className="mt-5 Home__part" style={{height:'100vh'}}>
        <div className="dynavac_img_part d-flex justify-content-center align-items-center flex-column">
          <img src={homeimg} alt="" />
          <SplitText
              text="CLEANER AIR, BETTERFUTURE"
              className="fs-3 font-semibold text-center"
              delay={150}
              animationFrom={{ opacity: 0, transform: 'translate3d(0,50px,0)' }}
              animationTo={{ opacity: 1, transform: 'translate3d(0,0,0)' }}
              easing="easeOutCubic"
              threshold={0.2}
              rootMargin="-50px"
              onLetterAnimationComplete={handleAnimationComplete}
            />
            <div className="description col-10 text-center mt-2">
              <p>
              Welcome to Dayanavac’s Official Employee Attendance Portal.
              Designed exclusively for our team, this app helps you log attendance, manage shift timings, and keep track of your daily work hours — all with just a few taps.
              Simple, secure, and built for our workforce.
              </p>
              <div className=" mt-5 gap-3 d-flex justify-content-center align-items-center flex-column">

              <h3>
              Stay punctual. Stay productive.
              </h3>
              <h3>
              Let’s build a better future, together.

              </h3>
              </div>
            </div>
        </div>
      
      </div>
    </section>
    </>
  )
}



export default Home






