import React, { useEffect, useState } from 'react';
import axios from 'axios';

const HomeTwo = () => {
    const [userDetails, setUserDetails] = useState(null);
    const [attendanceRecords, setAttendanceRecords] = useState([]);
    const [currentDateTime, setCurrentDateTime] = useState(new Date());
    const [selectedRecord, setSelectedRecord] = useState(null);
    const [showAllRecords, setShowAllRecords] = useState(false); // 👈 New state

    useEffect(() => {
        // Check Authentication
        axios.get('http://localhost:8000/check-auth', { withCredentials: true })
            .then(response => {
                if (response.data.authenticated) {
                    setUserDetails(response.data);

                    // Fetch Attendance
                    axios.get('http://localhost:8000/my-monthly-attendance', { withCredentials: true })
                        .then(res => setAttendanceRecords(res.data.records))
                        .catch(err => console.error('Attendance fetch error:', err));
                } else {
                    console.log("User not authenticated");
                }
            })
            .catch(error => {
                console.error('Error fetching user details:', error);
            });

        // Live Time
        const interval = setInterval(() => {
            setCurrentDateTime(new Date());
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    const handleSelectChange = (e) => {
        const selectedTaskName = e.target.value;
        const selected = attendanceRecords.find(r => r.task_name === selectedTaskName);
        setSelectedRecord(selected || null);
    };

    const toggleShowAllRecords = () => {
        setShowAllRecords(prev => !prev);
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                {userDetails ? (
                    <>
                        <h2 style={styles.title}>👋 Welcome, {userDetails.name}!</h2>
                        <p style={styles.info}><strong>Email:</strong> {userDetails.email}</p>

                        <div style={{ margin: '20px 0' }}>
                            <label htmlFor="taskDropdown"><strong>🗓️ Select Attendance Task:</strong></label>
                            <select id="taskDropdown" onChange={handleSelectChange} style={styles.select} defaultValue="">
                                <option value="" disabled>-- Select Task --</option>
                                {attendanceRecords.map((record, index) => (
                                    <option key={index} value={record.task_name}>
                                        {record.task_name} ({new Date(record.created_at).toLocaleDateString()})
                                    </option>
                                ))}
                            </select>
                        </div>

                        {selectedRecord && (
                            <div style={styles.detailsBox}>
                                <h3 style={styles.subtitle}>📋 Task Details:</h3>
                                <p><strong>Task Name:</strong> {selectedRecord.task_name}</p>
                                <p><strong>Place of Visit:</strong> {selectedRecord.place_of_visit}</p>
                                <p><strong>Purpose:</strong> {selectedRecord.purpose_of_visit}</p>
                                <p><strong>Time In:</strong> {selectedRecord.time_in}</p>
                                <p><strong>Time Out:</strong> {selectedRecord.time_out}</p>
                                <p><strong>Submitted At:</strong> {new Date(selectedRecord.created_at).toLocaleString()}</p>
                            </div>
                        )}

                        <button onClick={toggleShowAllRecords} className='submit'>
                            {showAllRecords ? 'Hide All Attendance Records' : 'Show All Attendance Records'}
                        </button>

                        {showAllRecords && (
                            <div style={{ marginTop: '20px', textAlign: 'left' }}>
                                <h3 className='' style={styles.subtitle}>📅 All Attendance Records:</h3>
                                {attendanceRecords.map((record, index) => (
                                    <div key={index} style={styles.detailsBox}>
                                        <p><strong>Task Name:</strong> {record.task_name}</p>
                                        <p><strong>Place:</strong> {record.place_of_visit}</p>
                                        <p><strong>Purpose:</strong> {record.purpose_of_visit}</p>
                                        <p><strong>Time In:</strong> {record.time_in}</p>
                                        <p><strong>Time Out:</strong> {record.time_out}</p>
                                        <p><strong>Submitted At:</strong> {new Date(record.created_at).toLocaleString()}</p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </>
                ) : (
                    <p style={styles.loading}>Loading user details...</p>
                )}
                <p style={styles.datetime}>🕒 {currentDateTime.toLocaleString()}</p>
            </div>
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: '#f0f4f8',
        padding: '20px',
    },
    card: {
        backgroundColor: '#fff',
        padding: '30px',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
        maxWidth: '600px',
        width: '100%',
        textAlign: 'center',
    },
    title: {
        marginBottom: '20px',
        fontSize: '1.8rem',
        color: '#333',
    },
    subtitle: {
        marginTop: '20px',
        marginBottom: '10px',
        fontSize: '1.4rem',
        color: '#222',
    },
    info: {
        marginBottom: '10px',
        fontSize: '1rem',
        color: '#555',
    },
    datetime: {
        marginTop: '20px',
        fontSize: '0.95rem',
        color: '#777',
    },
    loading: {
        fontSize: '1rem',
        color: '#888',
    },
    select: {
        marginTop: '10px',
        padding: '8px 12px',
        fontSize: '1rem',
        borderRadius: '6px',
        border: '1px solid #ccc',
        width: '100%',
    },
    button: {
        marginTop: '20px',
        padding: '10px 15px',
        fontSize: '1rem',
        borderRadius: '6px',
        border: 'none',
        backgroundColor: '#007BFF',
        color: '#fff',
        cursor: 'pointer',
    },
    detailsBox: {
        marginTop: '20px',
        textAlign: 'left',
        background: '#f9f9f9',
        padding: '15px',
        borderRadius: '8px',
        boxShadow: 'inset 0 0 5px rgba(0,0,0,0.05)',
    }
};

export default HomeTwo;
