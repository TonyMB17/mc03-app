const indicators = {
  mc03: {
    code: 'mc03',
    title: 'MC-03 Seguimiento Neonatal',
    shortName: 'MC-03',
    description: 'Paquete recien nacido: BCG, HvB, CRED y tamizaje neonatal.',
    defaultProvince: 'ABANCAY',
    defaultTarget: 70.7,
  },
  mc02: {
    code: 'mc02',
    title: 'MC-02 Paquete Integrado Infantil',
    shortName: 'MC-02',
    description: 'Menores de 12 meses con paquete integrado de servicios.',
    defaultProvince: 'ABANCAY',
    defaultTarget: 80.9,
  },
};

export const indicatorList = Object.values(indicators);
export default indicators;
