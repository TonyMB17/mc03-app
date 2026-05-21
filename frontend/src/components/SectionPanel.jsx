import { UsiCard } from './usi';

function SectionPanel({ children, className = '', as = 'section', ...props }) {
  return (
    <UsiCard as={as} className={className} {...props}>
      {children}
    </UsiCard>
  );
}

export default SectionPanel;
