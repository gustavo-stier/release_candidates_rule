import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import reactLogo from '../../assets/react.svg'
import viteLogo from '/vite.svg'
import './style.css'
import api from '../../services/api.js'

function Login() {
  const navigate = useNavigate()
  const inputEmail = useRef()
  const inputPassword = useRef()

  async function handleLogin() {
    try {
      const response = await api.post('/auth/login', {  
        email: inputEmail.current.value,
        password: inputPassword.current.value
      })
      
      // Se o login foi bem-sucedido, salva o token e redireciona
      if (response.status === 200) {
        // Salva o token no localStorage
        const token = response.data.token || response.data.access_token
        localStorage.setItem('token', token)
        
        navigate('/home')
      }
    } catch (error) {
      console.error('Erro ao fazer login:', error)
      alert('Erro ao fazer login. Verifique suas credenciais.')
    }
  }

  return (
    <>
      <div className='container'>
        <form className='login-form'>
          <h1>Login</h1>
          <div className='input-group'>
            <label htmlFor='email'>Email</label>
            <input type='text' id='email' name='email' required ref={inputEmail} />
          </div>
          <div className='input-group'>
            <label htmlFor='password'>Password</label>
            <input type='password' id='password' name='password' required ref={inputPassword} />
          </div>
          <button type='button' onClick={handleLogin}>Login</button>
        </form>
      </div>
    </>
  )
}

export default Login
