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

// Add scroll-based animations for elements with slide-up class
window.addEventListener( 'scroll', function ()
{
    const items = document.querySelectorAll( '.slide-up' );
    items.forEach( item =>
    {
        const top = item.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        if ( top < windowHeight - 80 )
        {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }
    } );
} );

// Initialize slide-up items

// Ripple effect helper
function createRipple ( e )
{
    const btn = e.currentTarget;
    const circle = document.createElement( 'span' );
    const diameter = Math.max( btn.clientWidth, btn.clientHeight );
    const radius = diameter / 2;
    circle.style.width = circle.style.height = `${ diameter }px`;
    circle.style.left = `${ e.clientX - btn.offsetLeft - radius }px`;
    circle.style.top = `${ e.clientY - btn.offsetTop - radius }px`;
    circle.classList.add( 'ripple' );
    const ripple = btn.getElementsByClassName( 'ripple' )[ 0 ];
    if ( ripple ) ripple.remove();
    btn.appendChild( circle );
}

// Launch simple confetti animation
function launchConfetti ()
{
    const container = document.createElement( 'div' );
    container.className = 'confetti-container';
    document.body.appendChild( container );
    const colors = [ '#FFC107', '#FF5722', '#4CAF50', '#2196F3', '#E91E63' ];
    for ( let i = 0; i < 80; i++ )
    {
        const conf = document.createElement( 'div' );
        conf.className = 'confetti';
        conf.style.left = Math.random() * 100 + '%';
        conf.style.backgroundColor = colors[ Math.floor( Math.random() * colors.length ) ];
        conf.style.animationDuration = ( 2 + Math.random() * 2 ) + 's';
        container.appendChild( conf );
    }
    setTimeout( () => container.remove(), 5000 );
}

// add classes on load for nice entrance
window.addEventListener( 'DOMContentLoaded', () =>
{
    document.querySelectorAll( '.fade-in' ).forEach( el => el.classList.add( 'fade-in' ) );
    document.querySelectorAll( 'button' ).forEach( btn => btn.addEventListener( 'click', createRipple ) );
    // if result page present and celebrate flag
    const resultCard = document.querySelector( '.score-display' );
    if ( resultCard && resultCard.classList.contains( 'celebrate' ) )
    {
        launchConfetti();
    }

    // quiz page logic: timer & progress
    const quizSection = document.querySelector( '.quiz-session' );
    if ( quizSection )
    {
        const questions = document.querySelectorAll( '.question-card' );
        const total = questions.length;
        const classLevel = document.querySelector( '.quiz-form' ).dataset.class || '3';

        // Calculate time per question based on class level
        let timePerQuestion = 20;  // default
        if ( classLevel === '1' || classLevel === '2' )
        {
            timePerQuestion = 30;  // easier, more time
        } else if ( classLevel === '3' || classLevel === '4' )
        {
            timePerQuestion = 20;  // medium
        } else if ( classLevel === '5' )
        {
            timePerQuestion = 15;  // harder, less time
        }

        const totalTime = total * timePerQuestion;
        let timeLeft = totalTime;
        const timerEl = document.getElementById( 'timer' );
        const timerFill = document.getElementById( 'timer-fill' );
        const progressBar = document.getElementById( 'progress-bar' );

        // Set initial timer display
        if ( timerEl ) timerEl.textContent = timeLeft;
        function updateProgress ()
        {
            const answered = document.querySelectorAll( '.quiz-form input[type=radio]:checked' ).length;
            const percent = total ? ( answered / total ) * 100 : 0;
            progressBar.style.width = percent + '%';
        }
        document.querySelectorAll( '.quiz-form input[type=radio]' ).forEach( r =>
        {
            r.addEventListener( 'change', () =>
            {
                updateProgress();
                // highlight the selected label
                const name = r.name;
                document.querySelectorAll( `input[name="${ name }"]` ).forEach( other =>
                {
                    const lbl = other.closest( 'label' );
                    if ( lbl ) lbl.classList.remove( 'selected' );
                } );
                const parentLabel = r.closest( 'label' );
                if ( parentLabel ) parentLabel.classList.add( 'selected' );
            } );
        } );
        updateProgress();
        const interval = setInterval( () =>
        {
            timeLeft -= 1;
            if ( timerEl ) timerEl.textContent = timeLeft;
            if ( timerFill ) timerFill.style.width = ( timeLeft / totalTime * 100 ) + '%';
            if ( timeLeft <= 0 )
            {
                clearInterval( interval );
                document.querySelector( '.quiz-form' ).submit();
            }
        }, 1000 );
    }
} );

// Initialize slide-up items for scroll animation
function initSlideUp ()
{
    document.querySelectorAll( '.slide-up' ).forEach( ( el, idx ) =>
    {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        el.style.transitionDelay = `${ idx * 0.1 }s`;
    } );
}

initSlideUp();
// Trigger initial animation check
setTimeout( () =>
{
    window.dispatchEvent( new Event( 'scroll' ) );
}, 100 );
