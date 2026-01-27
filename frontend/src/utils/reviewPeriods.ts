// Review period display names mapping
export const reviewPeriodLabels: Record<string, string> = {
  'DAILY': 'Daily',
  'DAILY_WEEKLY': 'Daily/Weekly',
  'WEEKLY': 'Weekly',
  'WEEKLY_MONTHLY': 'Weekly/Monthly',
  'MONTHLY': 'Monthly',
  'REGULAR': 'Regular',
  'REGULAR_MONTHLY': 'Regular - meeting monthly',
  'MONTHLY_QUARTERLY': 'Monthly/Quarterly',
  'QUARTERLY': 'Quarterly',
  'HALF_YEARLY_QUARTERLY': 'Half Yearly',
  'QUARTERLY_HALFYEARLY_ANNUALLY': 'Quarterly/Halfyearly/Annually',
  'ANNUALLY': 'Annually',
};

export const reviewPeriodOptions = [
  { value: 'DAILY', label: 'Daily' },
  { value: 'WEEKLY', label: 'Weekly' },
  { value: 'MONTHLY', label: 'Monthly' },
  { value: 'QUARTERLY', label: 'Quarterly' },
  { value: 'HALF_YEARLY_QUARTERLY', label: 'Half Yearly' },
  { value: 'ANNUALLY', label: 'Annually' },
];

export const getReviewPeriodLabel = (period: string): string => {
  return reviewPeriodLabels[period] || period;
};

