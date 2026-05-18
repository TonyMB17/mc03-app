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
  si02: {
    code: 'si02',
    title: 'SI-02 Hierro y Dosaje',
    shortName: 'SI-02',
    description: 'Suplementacion con hierro, dosajes de hemoglobina y termino de tratamiento por subindicador.',
    defaultProvince: 'ABANCAY',
    defaultTarget: 65,
    packageUpload: true,
    requiredFiles: 4,
    subindicators: [
      { code: 'si02_01', officialCode: 'SI-02.01', shortName: 'SI-02.01', title: 'Hierro 4 meses y dosaje 6 meses', target: 92 },
      { code: 'si02_02', officialCode: 'SI-02.02', shortName: 'SI-02.02', title: 'Prematuridad o bajo peso', target: 60.3 },
      { code: 'si02_03', officialCode: 'SI-02.03', shortName: 'SI-02.03', title: 'Doce meses con anemia', target: 55 },
      { code: 'si02_04', officialCode: 'SI-02.04', shortName: 'SI-02.04', title: 'Doce meses sin anemia', target: 65 },
    ],
  },
};

export const indicatorList = Object.values(indicators);
export default indicators;
