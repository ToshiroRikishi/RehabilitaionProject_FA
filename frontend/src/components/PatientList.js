import React from 'react';

const PatientList = ({ patients, onSelectPatient }) => {
  return (
    <div className="border p-4 rounded">
      <h2 className="text-xl font-semibold mb-2">Patients</h2>
      <ul>
        {patients.map(patient => (
          <li
            key={patient.code}
            className="cursor-pointer p-2 hover:bg-gray-100"
            onClick={() => onSelectPatient(patient.code)}
          >
            Patient Code: {patient.code}, Gender: {patient.gender}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PatientList;