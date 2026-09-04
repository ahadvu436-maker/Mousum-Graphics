import './Footer.css';

const SOCIALS = [
  { label: 'Instagram', href: 'https://instagram.com' },
  { label: 'Behance', href: 'https://behance.net' },
  { label: 'LinkedIn', href: 'https://linkedin.com' },
];

function Footer() {
  const year = new Date().getFullYear();
  
  return (
    <footer id="contact" className="footer">
      <span className="footer__crop footer__crop--tl" aria-hidden="true" />
      <span className="footer__crop footer__crop--tr" aria-hidden="true" />

      <div className="footer__inner">
        <div className="footer__contact">
          <h2 className="footer__headline">Let&apos;s start a project.</h2>
          <a href="mailto:hello@mousumgraphics.com" className="footer__email">
            hello@mousumgraphics.com
          </a>
        </div>

        <div className="footer__grid">
          <div className="footer__column">
            <h3 className="footer__label">Studio</h3>
            <p className="footer__text">Kolkata, India</p>
            <p className="footer__text">Working with clients worldwide</p>
          </div>

          <div className="footer__column">
            <h3 className="footer__label">Follow</h3>
            {SOCIALS.map((social) => (
              <a
                key={social.label}
                href={social.href}
                className="footer__link"
              >
                {social.label}
              </a>
            ))}
          </div>
        </div>
      </div>

      <div className="footer__bottom">
        <span>© {year} Mousum Graphics</span>
        <span>All work, all rights reserved</span>
      </div>
    </footer>
  );
}

export default Footer;