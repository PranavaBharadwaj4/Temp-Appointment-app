
import './App.css';
import {Routes, Route} from 'react-router-dom'
import Home from './components/Home';
import DoctorsSettings from './components/DoctorsSettings';
import DoctorsAuthView from './components/DoctorsAuthView';
import PatientAppointmentForm from './components/PatientAppointmentForm';


function App() {
  return <Routes>
    <Route path ='/' element={ <Home/>}/>
    <Route path ='/doctor-settings/' element={ <DoctorsSettings/>}/>
    <Route path ='/doctor-auth/' element={ <DoctorsAuthView/>}/>
    <Route path="/patient-book-appointment/:id" element={<PatientAppointmentForm/>} />

  </Routes>
}

export default App;
