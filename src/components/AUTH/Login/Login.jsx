import React, { useState } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../../Loading.css';
import './Login.css'; // Import your CSS file for styling


const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({ email: false, password: false });
  const [loading, setLoading] = useState(false);
  const [display, setDisplay] = useState('none');
  const [viewPassword, setViewPassword] = useState(false);
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showvalue, setShowvalue] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    let hasError = false;
    if (!email) {
      setErrors((prev) => ({ ...prev, email: true }));
      toast.error("Email is required.");
      hasError = true;
    }
    if (!password) {
      setErrors((prev) => ({ ...prev, password: true }));
      toast.error("Password is required.");
      hasError = true;
    }
    if (hasError) return;
  
    setLoading(true);
    setIsSubmitting(true);
  
    try {
      const response = await axios.post(
        "http://localhost:8000/login",
        { email, password },
        { withCredentials: true }
      );
  
      toast.success("Login successful!");
      
      // Delay for smoother UX or wait for cookies to settle (if needed)
      setTimeout(() => {
        navigate("/home");
        window.location.reload();
      }, 1000);
  
    } catch (err) {
      console.error("Login error:", err.response);
      const errorMessage = err.response?.data?.detail || "Invalid email or password.";
      toast.error(errorMessage);
      setDisplay("block");
    } finally {
      setLoading(false);
      setIsSubmitting(false);
    }
  };
  


 
  return (
    <>
      <ToastContainer />
      <section>
        <div className="login__part  d-flex flex-column justify-content-center aligen-items-center" style={{height:'85vh',width:'100%'}}>
      
          { loading ? ( 
             <div className="loadingspinner">
             <div id="square1"></div>
             <div id="square2"></div>
             <div id="square3"></div>
             <div id="square4"></div>
             <div id="square5"></div>
           </div>
          ) : (
          //    <form className="col-lg-6 col-md-6 col-10 mx-auto mt-5" onSubmit={handleSubmit}>
          //    <div className="mb-3">
          //      <label htmlFor="loginEmail" className="form-label">Email address</label>
          //      <input
          //        type="email"
          //        className="form-control"
          //        id="loginEmail"
          //        value={email}
          //        onChange={(e) => {
          //          setEmail(e.target.value);
          //          setErrors((prev) => ({ ...prev, email: false }));
          //        }}
          //        style={{ borderColor: errors.email ? 'red' : '' }}
          //      />
          //    </div>
          //    <div className="mb-3">
          //      <label htmlFor="loginPassword" className="form-label">Password</label>
          //      <input
          //        type="password"
          //        className="form-control"
          //        id="loginPassword"
          //        value={password}
          //        onChange={(e) => {
          //          setPassword(e.target.value);
          //          setErrors((prev) => ({ ...prev, password: false }));
          //        }}
          //        style={{ borderColor: errors.password ? 'red' : '' }}
          //      />
          //    </div>
 
          //    <button type="submit" className="btn btn-primary" disabled={loading}>
          //     submit
          //    </button>
 
          //    <div className="d-flex mt-3">
          //      <p className='me-2'>Don't have an account?</p>
          //      <Link to={'/register'}>Create Account</Link>
          //    </div>
          //    <div className="for_got_pass">
          //      <Link to={'/forgotpassword'}>Forgot Password?</Link>
          //    </div>
          //  </form>     
<div className="login__part d-flex justify-content-center"   >

<form 
      className="login-form gap-4 col-lg-4 col-md-6 col-10 d-flex flex-column justify-content-center" 
      onSubmit={handleSubmit}
      noValidate
    >   
      <h1 className="form-title">Login  your account</h1>
      
      <div className={`input-container ${errors.email ? 'error' : ''}`}>
        <input 
          placeholder="Enter email"   
          type="email"
          className="form-control login_input"
          id="loginEmail"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            setErrors(prev => ({ ...prev, email: false }));
          }}
          style={{ borderColor: errors.email ? 'red' : '' }}
          required
          aria-describedby="emailError"
        />
        <span className="input-icon">
          <svg stroke="currentColor" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round"></path>
          </svg>
        </span>
        {errors.email && (
          <span id="emailError" className="error-message">
            Please enter a valid email address
          </span>
        )}
      </div>
      
      <div className={`input-container p-0 login_input pass-outer form-control m-0 d-flex justify-content-between align-items-center ${errors.password ? 'error' : ''}`}>
        <input 
          placeholder="Enter password"   
          type={viewPassword ? "text" : "password"}
          className="form-control login_pass"
          id="loginPassword"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            setErrors(prev => ({ ...prev, password: false }));
          }}
          style={{ borderColor: errors.password ? 'red' : '' }}
          required
          minLength="6"
          aria-describedby="passwordError"
        />
        <button 
          onClick={() => setViewPassword(!viewPassword)} 
          className="eye-btn" 
          type="button"
          aria-label={viewPassword ? "Hide password" : "Show password"}
        >
          {viewPassword ? "🙈" : "👁"}
        </button>
      </div>
      {errors.password && (
          <span id="passwordError" className="error-message">
            Password must be at least 6 characters
          </span>
        )}

      <button 
        className="submit" 
        type="submit"
        disabled={isSubmitting}
      >
        {isSubmitting ? 'Logging in...' : 'Login'}
      </button>

      <p className="signup-link">
        No account?
        <a href="/register">Create Account</a>
      </p>
      <p className="signup-link mt-0">
       
        <a href="/forgotpassword">Forgot Password</a>
      </p>
    </form>
</div>

          )
          
        }
        </div>
        
      </section>
    </>
  );
};

export default Login;