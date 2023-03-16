import React from 'react'
import axios from 'axios';
import {useState, useEffect } from 'react';

function DoctorsSettings() {
  const [formData, setFormData] = useState({
    activeDays: 7,
    timeSlots: ['9:00 AM', '10:00 AM', '11:00 AM', '2:00 PM', '3:00 PM', '4:00 PM'],
    maxParticipants: 1,
  });
  
  const [start_time, setStartTime] = useState("");
  const [end_time, setEndTime] = useState("");
  const [link, setLink] = useState(null);
  const [go, setGo] = useState(0);


const getLink = () => {
  fetch('/api/link/')
    .then(response => response.json())
    .then(data => {
      const latestLink = data[data.length - 1];  // get the latest link object
      console.log(latestLink)
      setLink(`http://127.0.0.1:8000/patient-book-appointment/${latestLink['hash']}/`);  // save the link ID
    });
};

useEffect(() => {
  getLink();
}, [go]);

  
  // useEffect(() => {
  //   async function fetchData() {
  //     const response = await axios.get('/api/link/');
  //     setLink(response.data);
  //   }
  //   fetchData();
  // }, []);

  const handleCopyClick = () => {
    navigator.clipboard.writeText(link);
  };

  function incrementGo() {
    // Similar to this.setState({ fruit: 'orange' })
    const number = go;
    setGo(number+1);
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    const linkFormData = new FormData();
        linkFormData.append("timeslots",formData.timeSlots)
        linkFormData.append("days_valid",formData.activeDays)
        linkFormData.append("max_participants",formData.maxParticipants)
        linkFormData.append("start_time",start_time)
        linkFormData.append("end_time",start_time)
    try {
      await axios.post('/doctor-settings/', linkFormData);
      alert('Settings saved successfully!');
    } catch (err) {
      alert(`Error saving settings: ${err}`);
    }
    incrementGo();
    // ()=>{);
    // return null;}
  };

  return (
    <div>
      <h2>Appointment Link Settings</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="activeDays">Active Days:</label>
          <input
            type="number"
            id="activeDays"
            name="activeDays"
            value={formData.activeDays}
            onChange={(e) => setFormData({ ...formData, activeDays: e.target.value })}
          />
        </div>
        <div>
          <label htmlFor="timeSlots">Available Time Slots:</label>
          <select
            multiple
            id="timeSlots"
            name="timeSlots"
            value={formData.timeSlots}
            onChange={(e) =>
              setFormData({
                ...formData,
                timeSlots: [...e.target.options].filter((option) => option.selected).map((option) => option.value),
              })
            }
          >
            <option value="9:00 AM">9:00 AM</option>
            <option value="10:00 AM">10:00 AM</option>
            <option value="11:00 AM">11:00 AM</option>
            <option value="2:00 PM">2:00 PM</option>
            <option value="3:00 PM">3:00 PM</option>
            <option value="4:00 PM">4:00 PM</option>
          </select>
        </div>
        <div>
          <label htmlFor="maxParticipants">Max Participants:</label>
          <input
            type="number"
            id="maxParticipants"
            name="maxParticipants"
            value={formData.maxParticipants}
            onChange={(e) => setFormData({ ...formData, maxParticipants: e.target.value })}
          />
        </div>
        <div>
        <label htmlFor="start_time">Start time:</label>
        <input
          type="time"
          id="start_time"
          value={start_time}
          onChange={(event) => setStartTime(event.target.value)}
        />
      </div>
      <div>
        <label htmlFor="end_time">End time:</label>
        <input
          type="time"
          id="end_time"
          value={end_time}
          onChange={(event) => setEndTime(event.target.value)}
        />
      </div>
        <button type="submit">Save Settings</button>
      </form>
      <div>
      {go!==0 && (
        <button onClick={handleCopyClick}>
          Copy Link
        </button>
      )}
    </div>
    </div>
  );
}

export default DoctorsSettings;