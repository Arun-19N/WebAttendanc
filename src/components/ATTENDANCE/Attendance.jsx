import React, { useState } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import axios from 'axios';

const Attendance = () => {
  const [taskName, setTaskName] = useState('');
  const [placeVisit, setPlaceVisit] = useState('');
  const [purposeVisit, setPurposeVisit] = useState('');
  const [visitingPersonName, setVisitingPersonName] = useState('');
  const [message, setMessage] = useState('');
  const [employeeLocation, setEmployeeLocation] = useState('');
  const [employeeAddress, setEmployeeAddress] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [loadingLocation, setLoadingLocation] = useState(false);
  const [loading, setLoading] = useState(false);

  const getLocation = () => {
    setShowForm(true);
    setLoadingLocation(true);

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const lat = position.coords.latitude.toString();
          const lon = position.coords.longitude.toString();
          const coords = `${lat}, ${lon}`;
          setEmployeeLocation(coords);
          localStorage.setItem('latitude', lat);
          localStorage.setItem('longitude', lon);

          try {
            const res = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
            const data = await res.json();
            setEmployeeAddress(data.display_name || 'Address not found');
          } catch (error) {
            console.error('Error fetching address:', error);
            setEmployeeAddress('Error fetching address');
          }

          setLoadingLocation(false);
        },
        (error) => {
          console.error('Geolocation error:', error);
          setMessage('Unable to retrieve your location.');
          setLoadingLocation(false);
        }
      );
    } else {
      setMessage('Geolocation is not supported by this browser.');
      setLoadingLocation(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(
        'http://localhost:8000/attendance',
        {
          task_name: taskName,
          place_of_visit: placeVisit,
          purpose_of_visit: purposeVisit,
          visiting_person_name: visitingPersonName,
          employee_location: employeeLocation,
          employee_address: employeeAddress,
        },
        {
          withCredentials: true,
        }
      );

      setMessage(response.data.message || 'Attendance submitted successfully.');
      setShowForm(false);
    } catch (err) {
      console.error(err);
      setMessage('Error occurred while submitting the form.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <div className="admin__pannel__part d-flex justify-content-center align-items-center" style={{ height: '100vh' }}>
        <div style={{ width: '100%', maxWidth: '500px' }}>
          <h2 className="text-center">Submit Your Attendance</h2>

          <div className="d-flex justify-content-center">
            <button className="btn btn-primary mt-3" onClick={getLocation}>
              Open Form
            </button>
          </div>

          {message && <div className="alert alert-info mt-3">{message}</div>}
          {loadingLocation && <div className="text-center text-muted mt-2">📍 Fetching location...</div>}

          {loading && (
            <div className="text-center mt-3">
              <div className="spinner-border text-success" role="status">
                <span className="visually-hidden">Submitting...</span>
              </div>
              <div className="text-muted mt-2">Submitting your form...</div>
            </div>
          )}

          {showForm && !loading && (
            <form onSubmit={handleSubmit} className="mt-4">
              <h4 className="text-center mb-4">Visit Form</h4>

              <div className="mb-3">
                <label className="form-label">Task Name</label>
                <input
                  type="text"
                  className="form-control"
                  value={taskName}
                  required
                  onChange={(e) => setTaskName(e.target.value)}
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Place of Visit</label>
                <input
                  type="text"
                  className="form-control"
                  value={placeVisit}
                  required
                  onChange={(e) => setPlaceVisit(e.target.value)}
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Purpose of Visit</label>
                <input
                  type="text"
                  className="form-control"
                  value={purposeVisit}
                  required
                  onChange={(e) => setPurposeVisit(e.target.value)}
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Visiting Person Name</label>
                <input
                  type="text"
                  className="form-control"
                  value={visitingPersonName}
                  required
                  onChange={(e) => setVisitingPersonName(e.target.value)}
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Your Coordinates</label>
                <input type="text" className="form-control" value={employeeLocation} disabled />
              </div>

              <div className="mb-3">
                <label className="form-label">Detected Address</label>
                <textarea className="form-control" rows="2" value={employeeAddress} disabled />
              </div>

              <button type="submit" className="btn btn-success w-100">
                Submit
              </button>
            </form>
          )}
        </div>
      </div>
    </section>
  );
};

export default Attendance;


















