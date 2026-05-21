function UsiCard({ children, className = '', as: Component = 'section', ...props }) {
  return (
    <Component className={`card border border-base-300 bg-base-100 shadow-sm ${className}`.trim()} {...props}>
      {children}
    </Component>
  );
}

function Header({ children, className = '' }) {
  return <div className={`border-b border-base-300 p-4 ${className}`.trim()}>{children}</div>;
}

function Body({ children, className = '' }) {
  return <div className={`p-5 ${className}`.trim()}>{children}</div>;
}

function Footer({ children, className = '' }) {
  return <div className={`border-t border-base-300 p-4 ${className}`.trim()}>{children}</div>;
}

UsiCard.Header = Header;
UsiCard.Body = Body;
UsiCard.Footer = Footer;

export default UsiCard;
