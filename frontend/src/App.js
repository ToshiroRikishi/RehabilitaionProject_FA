import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PatientList from './components/PatientList';
import PatientDetails from './components/PatientDetails';
import ManualPrediction from './components/ManualPrediction';
import CreateCard from './components/CreateCard';
import './App.css';

const App = () => {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/patients')
      .then(response => setPatients(response.data))
      .catch(error => console.error('Error fetching patients:', error));
  }, []);

  const handleSelectPatient = async (code) => {
    try {
      const response = await axios.get(`http://localhost:8000/api/patients/${code}`);
      setSelectedPatient(response.data);
    } catch (error) {
      console.error('Error fetching patient details:', error);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">MoleScane Rehabilitation</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <PatientList patients={patients} onSelectPatient={handleSelectPatient} />
        <PatientDetails patient={selectedPatient} />
        <ManualPrediction />
        <CreateCard />
      </div>
    </div>
  );
};

export default App;