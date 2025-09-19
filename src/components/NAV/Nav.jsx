// Nav.jsx
import React, { useState, useEffect } from 'react';
import { Link, Routes, Route, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Home from '../HOME/Home';
import Login from '../AUTH/Login/Login';
import Register from '../AUTH/Register/Register';
import Attendance from '../ATTENDANCE/Attendance';
import ProtectedRoute from '../ProtectedRoute/ProtectedRoute';
import Otpverify from '../AUTH/OtpVerification/OtpVerification';
import Forgotpassword from '../AUTH/Login/Forgotpassword';
import ChangePassword from '../AUTH/Login/Changepassword';
import HomeTwo from '../HOME/HomeTwo';
import GuestRoute from '../ProtectedRoute/GustRouter';
import logo from '../../assets/Dynavac-logo-1.png';
import './Nav.css';
import GetLocation from '../Getlogation';

const Nav = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const getAuth = async () => {
      try {
        const response = await axios.get("http://localhost:8000/check-auth", {
          withCredentials: true,
        });

        setIsAuthenticated(response.data.authenticated);
      } catch (err) {
        console.error("Error in auth:", err);
        setIsAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    getAuth();
  }, []);

  const handleLogout = async () => {
    try {
      await axios.post("http://localhost:8000/logout", {}, {
        withCredentials: true,
      });

      setIsAuthenticated(false);
      navigate("/login");
        window.location.reload();
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <>
    <nav className="navbar navbar-expand-lg navbar-light bg-light">
  <div className="container-fluid">
    <div className="d-flex  nav__logo__button ">

    <Link className="navbar-brand" to="/home">
      <img src={logo} className="nav__logo" alt="Logo" />
    </Link>
    <button
      className="navbar-toggler "
      type="button"
      data-bs-toggle="collapse"
      data-bs-target="#navbarNav"
      aria-controls="navbarNav"
      aria-expanded="false"
      aria-label="Toggle navigation"
    >
      <span className="navbar-toggler-icon"></span>
    </button>
    </div>


    <div className="collapse navbar-collapse" id="navbarNav">
      <ul className="navbar-nav ms-auto">
        {isAuthenticated ? (
          <>
            <li className="nav-item">
              <Link className="nav-link" to="/home">Home</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/attendance">Attendance</Link>
            </li>
            <li className="nav-item">
              <button className="btn btn-link nav-link" onClick={handleLogout}>Logout</button>
            </li>
          </>
        ) : (
          <>
            <li className="nav-item">
              <Link className="nav-link" to="/">Home</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/login">Login</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/register">Register</Link>
            </li>
          </>
        )}
      </ul>
    </div>
  </div>
</nav>


      <Routes>
      {/* <Route element={<GuestRoute/>}
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path='/OtpVerification' element={<Otpverify/>}/>
      <Route path="/forgotpassword" element={<Forgotpassword/>} />
      <Route path="/passwordreset" element={<ChangePassword/>}/> */}
      {/* ✅ Protected route wrapper */}
      <Route element={<GuestRoute/>}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path='/OtpVerification' element={<Otpverify/>}/>
        <Route path="/forgotpassword" element={<Forgotpassword/>} />
        <Route path="/passwordreset" element={<ChangePassword/>}/>
      </Route>

      <Route element={<ProtectedRoute/>}>
        <Route path="/attendance" element={<Attendance />} />
        <Route path='/home' element={<HomeTwo/>} />
      </Route>
      <Route path='/Attendance2' element={<Attendance/>}/>
      <Route path="*" element={<div>404 Not Found</div>} />
    </Routes>
    </>
  );
};

export default Nav;
