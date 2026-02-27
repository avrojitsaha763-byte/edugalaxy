/**
 * EDUGALAXY - JavaScript File
 * Handles all interactive functionality
 */

/**
 * Toggle Sidebar - Opens/closes the slide-in sidebar
 */
function toggleSidebar ()
{
    const menuIcon = document.querySelector( '.menu-icon' );
    const sidebar = document.querySelector( '.sidebar' );
    const overlay = document.querySelector( '.sidebar-overlay' );

    menuIcon.classList.toggle( 'active' );
    sidebar.classList.toggle( 'active' );
    overlay.classList.toggle( 'active' );

    // Prevent body scroll when sidebar is open
    document.body.style.overflow = sidebar.classList.contains( 'active' ) ? 'hidden' : '';
}

/**
 * Close Sidebar - Closes the slide-in sidebar
 */
function closeSidebar ()
{
    const menuIcon = document.querySelector( '.menu-icon' );
    const sidebar = document.querySelector( '.sidebar' );
    const overlay = document.querySelector( '.sidebar-overlay' );

    menuIcon.classList.remove( 'active' );
    sidebar.classList.remove( 'active' );
    overlay.classList.remove( 'active' );

    // Restore body scroll
    document.body.style.overflow = '';
}

/**
 * Scroll to Top - Smooth scroll to the top of the page
 */
function scrollToTop ()
{
    window.scrollTo( {
        top: 0,
        behavior: 'smooth'
    } );
    closeSidebar();
}

/**
 * Start Learning - Action when CTA button is clicked
 */
function startLearning ()
{
    // Scroll to features section or trigger an action
    const featuresSection = document.querySelector( '#about' );
    if ( featuresSection )
    {
        featuresSection.scrollIntoView( { behavior: 'smooth' } );
    }

    // Optional: Add a fun alert or animation
    console.log( 'Starting learning adventure!' );
}

// ============================================
// Event Listeners
// ============================================

// Add smooth scroll for anchor links
document.querySelectorAll( 'a[href^="#"]' ).forEach( anchor =>
{
    anchor.addEventListener( 'click', function ( e )
    {
        const href = this.getAttribute( 'href' );
        if ( href !== '#' )
        {
            e.preventDefault();
            const target = document.querySelector( href );
            if ( target )
            {
                target.scrollIntoView( {
                    behavior: 'smooth',
                    block: 'start'
                } );
            }
        }
        closeSidebar();
    } );
} );

// Add scroll-based animations
window.addEventListener( 'scroll', function ()
{
    const cards = document.querySelectorAll( '.feature-card' );
    cards.forEach( ( card, index ) =>
    {
        const cardTop = card.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;

        if ( cardTop < windowHeight - 100 )
        {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }
    } );
} );

// Initialize cards with opacity for scroll animation
document.querySelectorAll( '.feature-card' ).forEach( ( card, index ) =>
{
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    card.style.transitionDelay = `${ index * 0.1 }s`;
} );

// Trigger initial animation check
setTimeout( () =>
{
    window.dispatchEvent( new Event( 'scroll' ) );
}, 100 );
