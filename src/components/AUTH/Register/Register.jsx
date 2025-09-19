import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../../Loading.css';
import './register.css';

const Register = () => {
  const [employeeId, setEmployeeId] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [designation, setDesignation] = useState('');
  const [loading, setLoading] = useState(false);

  const [errors, setErrors] = useState({
    name: false,
    email: false,
    password: false,
  });

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    let hasError = false;
    const newErrors = { name: false, email: false, password: false };

    const nameRegex = /^[A-Za-z\s]+$/;
    if (!nameRegex.test(name)) {
      newErrors.name = true;
      toast.error('Name can contain only alphabets and spaces.');
      hasError = true;
    }

    // const emailRegex = /^[^\s@]+@dynovec\.com$/;
    // if (!emailRegex.test(email)) {
    //   newErrors.email = true;
    //   toast.error('Please use a valid dynovec email (e.g. user@dynovec.com)');
    //   hasError = true;
    // }

    if (password.length < 8) {
      newErrors.password = true;
      toast.error('Password must be at least 8 characters long.');
      hasError = true;
    }

    setErrors(newErrors);
    if (hasError) {
      setLoading(false);
      return;
    }

    try {
      await axios.post('http://localhost:8000/register', {
        employee_id: employeeId,
        name,
        email,
        password,
        designation,
      });

      toast.success('Registration successful!');
      navigate('/OtpVerification', { state: { email } });
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Registration failed. Please try again.';
      toast.error(errorMsg);
    }

    setLoading(false);
  };

  return (
    <>
    <section >
      <ToastContainer />
      <div className="Register__part " >
 
          <form className="col-lg-6 col-md-6 col-10 mx-auto mt-3 pt-1 register-form" onSubmit={handleSubmit}>

             <h2 className="text-center">Register</h2>
            <p className="text-center">Please fill in the details below to create an account.</p>

            <div className="mb-3">
              <label htmlFor="employeeid" className="form-label">Employee Id</label>
              <input
                type="text"
                className="form-control register__inpute_focusd"
                id="employeeid"
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                required
              />
            </div>

            <div className="mb-3">
              <label htmlFor="name" className="form-label">Name</label>
              <input
                type="text"
                className="form-control register__inpute_focusd"
                id="name"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (/^[A-Za-z\s]*$/.test(e.target.value)) {
                    setErrors((prev) => ({ ...prev, name: false }));
                  }
                }}
                style={{ borderColor: errors.name ? 'red' : '' }}
                required
              />
            </div>

            <div className="mb-3">
              <label htmlFor="email" className="form-label">Email address</label>
              <input
                type="email"
                className="form-control register__inpute_focusd"
                id="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (/^[^\s@]+@dynovec\.com$/.test(e.target.value)) {
                    setErrors((prev) => ({ ...prev, email: false }));
                  }
                }}
                style={{ borderColor: errors.email ? 'red' : '' }}
                required
              />
            </div>

            <div className="mb-3">
              <label htmlFor="password" className="form-label">Password</label>
              <input   
                type="password"
                className="form-control register__inpute_focusd"
                id="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (e.target.value.length >= 8) {
                    setErrors((prev) => ({ ...prev, password: false }));
                  }
                }}
                style={{ borderColor: errors.password ? 'red' : '' }}
                required
              />
            </div>

            <div className="mb-3">
              <label htmlFor="designation" className="form-label">Designation</label>
              <select
                className="form-select register__inpute_focusd"
                id="designation"
                value={designation}
                onChange={(e) => setDesignation(e.target.value)}
                required
              >
                <option   value="">Select Designation</option>
                <option value="Manager">Manager</option>
                <option value="Developer">Developer</option>
                <option value="Tester">Tester</option>
              </select>
            </div>

            <div className="d-flex justify-content-center">
              <button  type="submit" className=" submit  mt-3">Submit</button>
            </div>

            <div className="d-flex mt-3 signup-link">
              <p className="me-2">Already have an account?</p>
              <Link to="/login">Login</Link>
            </div>
          </form>

      </div>
      {loading && (
                <div className="loadingspinner">
                    <div id="square1"></div>
                    <div id="square2"></div>
                    <div id="square3"></div>
                    <div id="square4"></div>
                    <div id="square5"></div>
                </div>
            )}
        
    </section>
    </>
  );
};

export default Register;
