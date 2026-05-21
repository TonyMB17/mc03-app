function UsiTabs({ tabs, activeTab, onChange, className = '' }) {
  return (
    <div role="tablist" className={`tabs tabs-lifted font-bold ${className}`.trim()}>
      {tabs.map((tab) => (
        <button
          key={tab.value}
          type="button"
          role="tab"
          className={`tab ${activeTab === tab.value ? 'tab-active text-primary' : 'text-base-content/60'}`}
          onClick={() => onChange(tab.value)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

export default UsiTabs;
