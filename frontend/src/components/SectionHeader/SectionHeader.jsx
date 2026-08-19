import './SectionHeader.css';

const SectionHeader = ({ title, description, badge }) => {
  return (
    <div className="section-header">
      <div>
        {badge ? <span className="section-badge">{badge}</span> : null}
        <h2>{title}</h2>
      </div>
      {description ? <p>{description}</p> : null}
    </div>
  );
};

export default SectionHeader;
