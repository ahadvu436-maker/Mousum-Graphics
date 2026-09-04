import './Hero.css';

const SERVICES = ['Identity', 'Editorial', 'Packaging', 'Motion'];

function Hero() {
  return (
    <section id="top" className="hero">
      <span className="hero__crop hero__crop--tl" aria-hidden="true" />
      <span className="hero__crop hero__crop--tr" aria-hidden="true" />
      <span className="hero__crop hero__crop--bl" aria-hidden="true" />
      <span className="hero__crop hero__crop--br" aria-hidden="true" />

      <div className="hero__inner">
        <h1 className="hero__headline">
          Graphic design for brands that want to be looked at twice.
        </h1>

        <p className="hero__sub">
          Mousum is a small studio building identities, editorial systems
          and packaging for clients who care about the details most people
          skip.
        </p>

        <ul className="hero__services">
          {SERVICES.map((service) => (
            <li key={service} className="hero__service">
              {service}
            </li>
          ))}
        </ul>
      </div>

      <a href="#work" className="hero__scroll">
        <span className="hero__scroll-line" aria-hidden="true" />
        View the work
      </a>
    </section>
  );
}

export default Hero;