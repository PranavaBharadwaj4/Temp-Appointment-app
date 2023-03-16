import React from 'react'

function DoctorsAuthView() {
  return (<>
    <h1>Hi, Doc!</h1>
    <h2>Mind logging in?</h2>
    <a href="http://127.0.0.1:8000/accounts/google/login/?process=login">Google</a>
  </>

  )
}

export default DoctorsAuthView