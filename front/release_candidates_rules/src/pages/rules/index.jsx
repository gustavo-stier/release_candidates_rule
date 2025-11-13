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