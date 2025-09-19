import React from 'react';
import './Footer.css';
import logo from '../../assets/dynavac-logo-1.png';

const Footer = () => {
  return (
    <>
      <section className='mt-5'>
          <div className="footer__part">
            <div className="container">

            <div className="footer_1 d-flex row ">

              <div className="img__and__content col-lg-6 col-md-12 ">
                <div className="footer__img__part">
                   <img src={logo} alt=""  style={{width:'30%'}}/>
                </div>
                <div className="footer__content__part mt-5">
              <div className="footer__content w-50">
                <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Facere ab cumque, officia minus voluptate ipsum voluptatibus! Quam libero tempore, provident suscipit architecto, ab unde temporibus minima nisi quas commodi. Rem.</p>
              </div>
            </div>
              </div>


              <div className=" footer__links  d-lg-flex  aligen-items-center justify-content-center  ms-auto gap-5 col-lg-6 col-md-12  ">
                   
                   
                    <div className="contact__info__footer footer__links__2 my-auto mx-auto text-center">
                      <h4>Contact</h4>
                       <div className="footer__number  ">
                       <i class="fa-solid fa-phone"></i> <span className='ms-2'> 8925633819 </span>,<span>8428424434</span><br />
                       <i class="fa-solid fa-envelope"></i> <span className='ms-2'>grano@gmail.com</span> 
                       <div className="adress d-flex w-lg-50 ">
                       <i class="fa-solid fa-location-dot mt-2"></i>  <p className='ms-3'>  Lorem ipsum dolor sit, amet consectetur adipisicing elit. Saepe eaque itaque modi perspiciatis, ipsum quae, neque quidem rem maiores dolorum quos! 
                       </p>
                     
                       </div>

                       </div>
                    </div>

              </div>


            </div>
           


            <div className="footer__icons__part">
                <div className="footer__icons text-lg-start text-md-start text-center">
               <link rel="stylesheet" href=""/> <i class="fa-brands fa-instagram"></i><i class="fa-brands fa-square-facebook"></i><i class="fa-brands fa-whatsapp"></i><i class="fa-brands fa-x-twitter"></i>
                </div>
              </div>
            </div>
          </div>
      </section>
    </>
  )
}

export default Footer
