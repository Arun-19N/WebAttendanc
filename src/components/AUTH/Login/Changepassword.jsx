import React, { useState } from "react";
import axios from "axios";
import { useSearchParams } from "react-router-dom";
import { useNavigate } from "react-router-dom";

const ChangePassword = () => {
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();

    const token = searchParams.get("token");

    const handleChangePassword = async (e) => {
        e.preventDefault();

        if (newPassword !== confirmPassword) {
            setMessage("New password and confirm password do not match.");
            return;
        }

        setLoading(true); // Start loader

        try {
            const response = await axios.post("http://localhost:8000/password-reset", {
                token,
                new_password: newPassword,
            });

            if (response.data.success) {
                setMessage("✅ Password changed successfully.");
                setTimeout(() => {
                   
                }, 2000);
            } else {
                setMessage(response.data.error || response.data.message || "❌ Failed to change password.");
            }
        } catch (error) {
            setMessage(error.response?.data?.detail || "❌ An error occurred.");
        } finally {
            navigate("/login");
            setLoading(false); // Stop loader
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h2 style={styles.title}>🔒 Reset Password</h2>
                <form onSubmit={handleChangePassword} style={styles.form}>
                    <label style={styles.label}>New Password</label>
                    <input
                        type="password"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        required
                        style={styles.input}
                        disabled={loading}
                    />

                    <label style={styles.label}>Confirm Password</label>
                    <input
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                        style={styles.input}
                        disabled={loading}
                    />

                    <button type="submit" className="submit" style={{  opacity: loading ? 0.6 : 1 }} disabled={loading}>
                        {loading ? "Resetting..." : "Reset Password"}
                    </button>
                </form>
                {message && (
                    <p style={{
                        ...styles.message,
                        color: message.startsWith("✅") ? "green" : "#ff4444"
                    }}>
                        {message}
                    </p>
                )}
            </div>
        </div>
    );
};

const styles = {
    container: {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        backgroundColor: "#f0f2f5",
    },
    card: {
        backgroundColor: "#fff",
        padding: "30px",
        borderRadius: "10px",
        boxShadow: "0 2px 10px rgba(0, 0, 0, 0.1)",
        width: "100%",
        maxWidth: "400px",
    },
    title: {
        marginBottom: "20px",
        textAlign: "center",
        fontSize: "1.5rem",
    },
    form: {
        display: "flex",
        flexDirection: "column",
    },
    label: {
        marginBottom: "5px",
        fontWeight: "500",
    },
    input: {
        marginBottom: "15px",
        padding: "10px",
        fontSize: "16px",
        borderRadius: "5px",
        border: "1px solid #ccc",
    },
    button: {
        padding: "10px",
        fontSize: "16px",
        backgroundColor: "#4CAF50",
        color: "white",
        border: "none",
        borderRadius: "5px",
        cursor: "pointer",
    },
    message: {
        marginTop: "15px",
        textAlign: "center",
        fontWeight: "bold",
    },
};

export default ChangePassword;
