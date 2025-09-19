import React, { useState, useEffect } from 'react';
import OtpInput from 'react-otp-input';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';

const Otpverify = () => {
    const [code, setCode] = useState('');
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [timer, setTimer] = useState(180); // 3 minutes
    const [resendDisabled, setResendDisabled] = useState(true);
     const [loading, setLoading] = useState(false);

    const navigate = useNavigate();
    const location = useLocation();
    const email = location.state?.email;

    // Redirect if email not found
    useEffect(() => {
        if (!email) {
            alert("Email not found. Please register again.");
            navigate('/register');
        }
    }, [email, navigate]);

    // Countdown timer logic
    useEffect(() => {
        if (timer <= 0) {
            setResendDisabled(false);
            return;
        }

        const interval = setInterval(() => {
            setTimer((prev) => prev - 1);
        }, 1000);

        return () => clearInterval(interval);
    }, [timer]);

    const formatTime = (seconds) => {
        const min = Math.floor(seconds / 60);
        const sec = seconds % 60;
        return `${min}:${sec < 10 ? '0' + sec : sec}`;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await axios.post("http://localhost:8000/verify-registration", {
                email,
                code
            });

            setMessage(response.data.message);
            setError('');

            if (response.data.message === "User verified and successfully registered.") {
                navigate('/login');
            }
        } catch (err) {
            const msg = err?.response?.data?.detail || "Something went wrong!";
            setError(msg);
            setMessage('');
        }finally{
            setLoading(false);
        }
    };

    const handleResend = async () => {
        try {
            const response = await axios.post("http://localhost:8000/resend-verification-code", {
                email
            });

            setMessage(response.data.message || "OTP resent successfully.");
            setCode('');
            setTimer(180);
            setResendDisabled(true);
            setError('');
        } catch (err) {
            const msg = err?.response?.data?.detail || "Failed to resend OTP";
            setError(msg);
            setMessage('');
        }
    };

    return (
        <section>
            <div className="otp__part d-flex flex-column align-items-center justify-content-center" style={{ height: '85vh' }}>
                <form onSubmit={handleSubmit}>
                    <h2 className="text-center mb-4">Verify OTP</h2>

                    <OtpInput
                        value={code}
                        onChange={setCode}
                        numInputs={6}
                        renderSeparator={<span>-</span>}
                        renderInput={(props) => (
                            <input
                                {...props}
                                className="otp-box fs-1 mx-2 text-center"
                                style={{
                                    width: "3rem",
                                    height: "3rem",
                                    fontSize: "1.5rem",
                                    borderRadius: "5px",
                                    border: "1px solid #ccc"
                                }}
                            />
                        )}
                    />

                    <div className="d-flex justify-content-center mt-4">
                        <button
                            type="submit"
                            className="submit"
                            style={{backgroundColor:' darkorange'}}
                            disabled={code.length !== 6}
                        >
                            Submit
                        </button>
                    </div>

                    <div className="mt-3 text-center">
                        {resendDisabled ? (
                            <p>Resend OTP in: <strong>{formatTime(timer)}</strong></p>
                        ) : (
                            <button type="button" className="btn btn-link p-0" onClick={handleResend}>
                                Resend OTP
                            </button>
                        )}
                    </div>

                    {message && (
                        <p className="mt-3 text-center text-success">{message}</p>
                    )}
                    {error && (
                        <p className="mt-3 text-center text-danger">{error}</p>
                    )}
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
    );
};

export default Otpverify;
