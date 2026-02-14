import { useState } from "react"

function Login() {
    const [email, setEmail] = useState<string>("")
    const [password, setPassword] = useState<string>("")

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        alert(`Logging in with ${email}`)
    }

    return(
        <div style={{maxWidth: "400px"}} >
            <h2>Login</h2>

            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: "10px" }}>
                    <label>Email</label><br />
                    <input 
                        type="email"
                        value={email}
                        onChange={e => setEmail(e.target.value)} 
                    />
                </div>

                 <div style={{ marginBottom: "10px" }}>
                    <label>Password</label><br />
                    <input 
                        type="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)} />
                 </div>

                 <button type="submit">Login</button>
            </form>
        </div>
    )
}

export default Login