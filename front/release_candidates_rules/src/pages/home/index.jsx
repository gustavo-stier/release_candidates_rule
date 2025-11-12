import { useState } from 'react'
import api from '../../services/api.js'
import "./style.css";

function Home() {
  const [ruleOptions, setRuleOptions] = useState([])
  const [activeTab, setActiveTab] = useState('config')

  async function loadRuleDefinitions() {
    try {
      const response = await api.get('/rules/definitions')
      if (response.status === 200) {
        // response.data é o objeto { transaction: [...], document: [...], ... }
        setRuleOptions(Object.keys(response.data))
      }
    } catch (error) {
      console.error('Erro ao carregar definições de regra:', error)
      alert('Não foi possível carregar as opções de regra.')
    }
  }

  const tabs = [
    { id: 'config', label: '⚙️ Configurações', icon: '⚙️' },
    { id: 'rules', label: '📋 Regras', icon: '📋' },
    { id: 'history', label: '📜 Histórico', icon: '📜' },
    { id: 'users', label: '👥 Usuários', icon: '👥' },
  ]

  return (
    <div className="home-layout">
      {/* Menu Lateral */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Menu</h2>
        </div>
        <nav className="sidebar-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`sidebar-item ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="sidebar-icon">{tab.icon}</span>
              <span className="sidebar-label">{tab.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Conteúdo Principal */}
      <main className="main-content">
        {activeTab === 'config' && (
          <div className="gateway-page">
        <div className="gateway-card">
            <div className="gateway-card-header">
                <h2>⚙️ Configurar Gateway e Regra</h2>
                <p>Escolha um gateway e a regra que deseja aplicar</p>
            </div>
            <div className="gateway-card-content">
                <div className="gateway-grid">
                    <div>
                        <label className="gateway-label">Gateway</label>
                        <input 
                            type="number" 
                            className="gateway-select" 
                            placeholder="Digite o gateway"
                        />
                    </div>
                    <div>
                        <label className="gateway-label">Regra</label>
                        <select className="gateway-select" onClick={loadRuleDefinitions}>
                            <option>Selecione uma regra</option>
                            {ruleOptions.map((rule) => (
                                <option key={rule} value={rule}>
                                    {rule}
                                </option>
                            ))}
                        </select>
                        <p className="gateway-description">
                            Mapeamento de identificador de pagamento
                        </p>
                    </div>
                </div>

                <div className="gateway-map-section">
                    <div className="gateway-map-header">
                        <h3>Mapeamento de Campos JSON</h3>
                    </div>
                    <p className="gateway-map-sub">
                        Configure o caminho de cada campo no JSON retornado pelo gateway
                    </p>
                    <div className="gateway-grid">
                        <div>
                            <label className="gateway-label">Payment ID</label>
                            <input className="gateway-input" placeholder="ex: data.payment.id" />
                        </div>
                        <div>
                            <label className="gateway-label">Valor</label>
                            <input className="gateway-input" placeholder="ex: data.amount" />
                        </div>
                    </div>
                </div>

                <div style={{ textAlign: "right" }}>
                    <button className="gateway-button">
                        ✅ Salvar Configuração
                    </button>
                </div>
            </div>
        </div>

        <div className="gateway-card">
            <div className="gateway-card-header">
                <h2>Configurações Salvas</h2>
                <p>Histórico de gateways e regras configurados</p>
            </div>
            <div className="gateway-card-content">
                <div className="gateway-saved-block">
                    <div className="gateway-saved-top">
                        <div className="gateway-saved-info">
                            <div>
                                <div>Gateway</div>
                                <strong>Gateway Principal</strong>
                            </div>
                            <div>→</div>
                            <div>
                                <div>Regra</div>
                                <strong>Payment ID</strong>
                            </div>
                        </div>
                        <span className="gateway-saved-tag">Configuração #1</span>
                    </div>

                    <div className="gateway-saved-fields">
                        <div className="gateway-saved-fields-title">Mapeamentos:</div>
                        <div className="gateway-grid">
                            <div className="gateway-saved-field">
                                <span>Payment ID:</span>
                                <code>data.payment.id</code>
                            </div>
                            <div className="gateway-saved-field">
                                <span>Valor:</span>
                                <code>data.amount</code>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
          </div>
        )}

        {activeTab === 'rules' && (
          <div className="gateway-page">
            <h2>📋 Regras</h2>
            <p>Conteúdo da aba de Regras</p>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="gateway-page">
            <h2>📜 Histórico</h2>
            <p>Conteúdo da aba de Histórico</p>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="gateway-page">
            <h2>👥 Usuários</h2>
            <p>Conteúdo da aba de Usuários</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default Home;
