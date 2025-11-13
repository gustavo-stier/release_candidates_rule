import { useState } from "react";
import api from "../../services/api.js";
import "./style.css";

function Home() {
  const [ruleOptions, setRuleOptions] = useState([]);
  const [activeTab, setActiveTab] = useState("config");
  const [selectedRule, setSelectedRule] = useState("");
  const [ruleFields, setRuleFields] = useState([]);
  const [fieldValues, setFieldValues] = useState({});
  const [gatewayId, setGatewayId] = useState("");
  const [gatewayName, setGatewayName] = useState("");
  const [tolerance, setTolerance] = useState({
    "max_local_amount": 0,
    "min_local_amount": 0,
    "plus_days":0,
    "min_days": 0
  });
  const [enabled, setEnabled] = useState(true);

  async function loadRuleDefinitions() {
    try {
      const response = await api.get("/rules/definitions");
      if (response.status === 200) {
        // response.data é o objeto { transaction: [...], document: [...], ... }
        setRuleOptions(Object.keys(response.data));
      }
    } catch (error) {
      console.error("Erro ao carregar definições de regra:", error);
      alert("Não foi possível carregar as opções de regra.");
    }
  }

  async function handleRuleChange(event) {
    const ruleName = event.target.value;
    setSelectedRule(ruleName);

    if (!ruleName || ruleName === "Selecione uma regra") {
      setRuleFields([]);
      setFieldValues({});
      return;
    }

    try {
      const response = await api.get(`/rules/definitions/${ruleName}`);
      if (response.status === 200) {
        const fields = response.data.composite_fields || [];
        setRuleFields(fields);

        // Inicializa os valores dos campos vazios
        const initialValues = {};
        fields.forEach((field) => {
          initialValues[field] = "";
        });
        setFieldValues(initialValues);
      }
    } catch (error) {
      console.error("Erro ao carregar campos da regra:", error);
      alert("Não foi possível carregar os campos da regra.");
    }
  }

  function handleFieldChange(fieldName, value) {
    setFieldValues((prev) => ({
      ...prev,
      [fieldName]: value,
    }));
  }

  async function handleCreateRule() {
    // Validações
    if (!gatewayId) {
      alert("Por favor, digite o Gateway ID.");
      return;
    }

    if (!gatewayName) {
      alert("Por favor, digite o Gateway Name.");
      return;
    }

    if (!selectedRule) {
      alert("Por favor, selecione uma regra.");
      return;
    }

    // Verifica se todos os campos obrigatórios foram preenchidos
    const missingFields = ruleFields.filter(
      (field) => !fieldValues[field] || fieldValues[field].trim() === ""
    );
    if (missingFields.length > 0) {
      alert(
        `Por favor, preencha os seguintes campos: ${missingFields.join(", ")}`
      );
      return;
    }

    // Monta o payload para enviar ao backend
    const rulePayload = {
      gateway_id: parseInt(gatewayId),
      gateway_name: gatewayName,
      rule_name: selectedRule,
      enabled: enabled,
      composite_key: ruleFields, // Os campos da regra são as composite_keys
      field_paths: fieldValues, // Os valores mapeados são os field_paths
      tolerance: tolerance,
    };

    try {
      const response = await api.post("/rules/insert-rule", rulePayload);

      if (response.status === 200) {
        alert(`Regra criada com sucesso! ID: ${response.data.rule_id}`);

        // Limpa os campos após sucesso
        setGatewayId("");
        setGatewayName("");
        setSelectedRule("");
        setRuleFields([]);
        setFieldValues({});
        setTolerance({
          "max_local_amount": 0,
          "min_local_amount": 0,
          "plus_days": 0,
          "min_days": 0
        });
      }
    } catch (error) {
      console.error("Erro ao criar regra:", error);
      const errorMessage =
        error.response?.data?.detail || "Erro ao criar regra. Tente novamente.";
      alert(errorMessage);
    }
  }

  const tabs = [
    { id: "config", label: "Configurações", icon: "⚙️" },
    { id: "rules", label: "Regras", icon: "📋" },
    { id: "users", label: "Usuários", icon: "👥" },
  ];

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
                        className={`sidebar-item ${activeTab === tab.id ? "active" : ""}`}
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
            {activeTab === "config" && (
                <div className="gateway-page">
                    <div className="gateway-card">
                        <div className="gateway-card-header">
                            <h2>⚙️ Configurar Gateway e Regra</h2>
                            <p>Escolha um gateway e a regra que deseja aplicar</p>
                        </div>
                        <div className="gateway-card-content">
                            <div className="gateway-grid">
                                <div>
                                    <label className="gateway-label">Gateway ID</label>
                                    <input
                                        type="number"
                                        className="gateway-select"
                                        placeholder="Digite o gateway ID"
                                        value={gatewayId}
                                        onChange={(e) => setGatewayId(e.target.value)}
                                    />
                                </div>
                                <div>
                                    <label className="gateway-label">Gateway Name</label>
                                    <input
                                        type="text"
                                        className="gateway-select"
                                        placeholder="Digite o nome do gateway"
                                        value={gatewayName}
                                        onChange={(e) => setGatewayName(e.target.value)}
                                    />
                                </div>
                                <div>
                                    <label className="gateway-label">Regra</label>
                                    <select
                                        className="gateway-select"
                                        onClick={loadRuleDefinitions}
                                        onChange={handleRuleChange}
                                        value={selectedRule}
                                    >
                                        <option value="">Selecione uma regra</option>
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
                                <div>
                                    <label className="gateway-label">
                                        <input
                                            type="checkbox"
                                            checked={enabled}
                                            onChange={(e) => setEnabled(e.target.checked)}
                                            style={{ marginRight: "8px" }}
                                        />
                                        Regra Ativada
                                    </label>
                                </div>
                            </div>

                            {ruleFields.length > 0 && (
                                <div className="gateway-map-section">
                                    <div className="gateway-map-header">
                                        <h3>Mapeamento de Campos JSON</h3>
                                    </div>
                                    <p className="gateway-map-sub">
                                        Configure o caminho de cada campo no JSON retornado pelo
                                        gateway
                                    </p>
                                    <div className="gateway-grid">
                                        {ruleFields.map((field) => (
                                            <div key={field}>
                                                <label className="gateway-label">
                                                    {field.charAt(0).toUpperCase() +
                                                        field.slice(1).replace(/_/g, " ")}
                                                </label>
                                                <input
                                                    className="gateway-input"
                                                    placeholder={`ex: data.${field}`}
                                                    value={fieldValues[field] || ""}
                                                    onChange={(e) =>
                                                        handleFieldChange(field, e.target.value)
                                                    }
                                                />
                                            </div>
                                        ))}
                                    </div>

                                    <hr
                                        style={{
                                            margin: "32px 0",
                                            border: "none",
                                            borderTop: "2px solid #eee",
                                        }}
                                    />

                                    <div className="tolerance-map-header">
                                        <h3>Tolerance</h3>
                                    </div>
                                    <p className="gateway-map-sub">
                                        Configure a tolerância do método
                                    </p>
                                    <div className="tolerance-grid">
                                        <div>
                                            <label className="tolerance-max-amount">
                                                Max Local Amount
                                            </label>
                                            <input
                                                type="number"
                                                className="tolerance-max-amount-input"
                                                placeholder="0"
                                                value={tolerance["max_local_amount"]}
                                                onChange={(e) => setTolerance({
                                                    ...tolerance,
                                                    "max_local_amount": Number(e.target.value)
                                                })}
                                            />
                                        </div>
                                        <div>
                                            <label className="tolerance-minimum-amount">
                                                Min Local Amount
                                            </label>
                                            <input
                                                type="number"
                                                className="tolerance-minimum-amount-input"
                                                placeholder="0"
                                                value={tolerance["min_local_amount"]}
                                                onChange={(e) => setTolerance({
                                                    ...tolerance,
                                                    "min_local_amount": Number(e.target.value)
                                                })}
                                            />
                                        </div>
                                        <div>
                                            <label className="date-minus-tolerance-range">Minus Days</label>
                                            <input
                                                type="number"
                                                className="date-minus-tolerance-range-input"
                                                placeholder="0"
                                                value={tolerance["min_days"]}
                                                onChange={(e) => setTolerance({
                                                    ...tolerance,
                                                    "min_days": Number(e.target.value)
                                                })}
                                            />
                                        </div>
                                        <div>
                                            <label className="date-plus-tolerance-range">
                                                Plus Days
                                            </label>
                                            <input
                                                type="number"
                                                className="date-plus-tolerance-range-input"
                                                placeholder="0"
                                                value={tolerance["plus_days"]}
                                                onChange={(e) => setTolerance({
                                                    ...tolerance,
                                                    "plus_days": Number(e.target.value)
                                                })}
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div style={{ textAlign: "right" }}>
                                <div className="spacer">
                                </div>
                            </div>
                            <div style={{ textAlign: "right" }}>
                                <button className="gateway-button" onClick={handleCreateRule}>
                                    Create Rule
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === "rules" && (
                <div className="gateway-page">
                    <h2>📋 Regras</h2>
                    <p>Conteúdo da aba de Regras</p>
                </div>
            )}

            {activeTab === "users" && (
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
