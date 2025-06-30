import React from 'react';

const PatientDetails = ({ patient }) => {
  if (!patient) return <div className="border p-4 rounded">Select a patient</div>;

  return (
    <div className="border p-4 rounded">
      <h2 className="text-xl font-semibold mb-2">Patient Details</h2>
      <p>Code: {patient.code}</p>
      <p>Info: {patient.patient_info}</p>
    </div>
  );
};

export default PatientDetails;