export const DEDUCTION_SECTIONS = {
  "80C": {
    limit: 150000,
    description: "Investments in PPF, ELSS, LIC, etc.",
  },
  "80CCD_1B": {
    limit: 50000,
    description: "Additional NPS contribution",
  },
  "80D": {
    limit: 100000,
    description: "Health insurance premium",
  },
  "80E": {
    limit: Infinity,
    description: "Education loan interest",
  },
};

export const TAX_SLABS_2024_25 = {
  old_regime: [
    { range: "0 - 2.5L", rate: "0%" },
    { range: "2.5L - 5L", rate: "5%" },
    { range: "5L - 10L", rate: "20%" },
    { range: "10L+", rate: "30%" },
  ],
  new_regime: [
    { range: "0 - 3L", rate: "0%" },
    { range: "3L - 7L", rate: "5%" },
    { range: "7L - 10L", rate: "10%" },
    { range: "10L - 12L", rate: "15%" },
    { range: "12L - 15L", rate: "20%" },
    { range: "15L+", rate: "30%" },
  ],
};