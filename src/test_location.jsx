import React, { useState, useEffect } from "react";

// Function to fetch the user's location using Geolocation API
const getUserLocation = async () => {
  if (navigator.geolocation) {
    return new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          resolve({ latitude, longitude });
        },
        (error) => reject(error)
      );
    });
  } else {
    throw new Error("Geolocation is not supported by this browser.");
  }
};

// Function to fetch address from Google Maps API
const getAddressFromCoordinates = async (lat, lng, apiKey) => {
  const url = `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${apiKey}`;
  
  const response = await fetch(url);
  const data = await response.json();
  if (data.status === "OK") {
    return data.results[0]?.formatted_address || "Address not found";
  } else {
    throw new Error("Unable to fetch address");
  }
};

const LocationComponent = () => {
  const [location, setLocation] = useState(null);
  const [address, setAddress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const apiKey = "YOUR_GOOGLE_MAPS_API_KEY"; // Replace with your API key

  useEffect(() => {
    const fetchLocationData = async () => {
      try {
        // Get user's location (coordinates)
        const { latitude, longitude } = await getUserLocation();
        
        // Get address from coordinates
        const userAddress = await getAddressFromCoordinates(latitude, longitude, apiKey);
        
        setLocation({ latitude, longitude });
        setAddress(userAddress);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchLocationData();
  }, [apiKey]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <h3>Your Location</h3>
      <p>Latitude: {location.latitude}</p>
      <p>Longitude: {location.longitude}</p>
      <p>Address: {address}</p>
    </div>
  );
};

export default LocationComponent;
