import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');
        setLoading(true);
        try {
            const response = await axios.post(
                'http://localhost:8000/password-reset-request',
                { email },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );
            setMessage(response.data.message);
           
        } catch (err) {
            const errorMsg =
                err.response?.data?.detail || err.response?.data?.message || 'Something went wrong';
            setError(errorMsg);
        }finally {
            setLoading(false);
          }
    };

    return (
        <>
        <div className="forgot__pass_part d-flex justify-content-center align-items-center " style={{ height: '85vh' }}>
            <div className="forgot-password-container p-4 shadow rounded" style={{ maxWidth: '400px', width: '100%' }}>
                <h2 className="mb-3 text-center">Forgot Password</h2>


                
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label htmlFor="email" className="form-label ">Email</label>
                        <input
                            type="email"
                            className="form-control login_input p-3"
                            id="email"
                            placeholder="Enter your email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="submit">Submit</button>
                </form>
                {message && <p className="text-success mt-3">{message}</p>}
                {error && <p className="text-danger mt-3">{error}</p>}
            </div>
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
        
        </>
    );
};

export default ForgotPassword;
