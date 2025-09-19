import React, { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import axios from 'axios';

const ProtectedRoute = () => {
  const [isVerified, setIsVerified] = useState(null);

  useEffect(() => {
    const verifyUser = async () => {
      try {
        const response = await axios.get('http://localhost:8000/check-auth', {
          withCredentials: true,
        });

        if (response.data.authenticated) {
          setIsVerified(true);
        } else {
          setIsVerified(false);
        }
      } catch (err) {
        console.error('Error verifying user', err);
        setIsVerified(false);
      }
    };

    verifyUser();
  }, []);

  if (isVerified === null) {
    return <div>Loading...</div>;
  }

  return isVerified ? <Outlet /> : <Navigate to="/" />;
};

export default ProtectedRoute;
