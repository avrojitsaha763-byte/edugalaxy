let timeLeft = 30;
let timer = setInterval( function ()
{
    document.getElementById( "timer" ).innerText = timeLeft;
    timeLeft--;
    if ( timeLeft < 0 )
    {
        clearInterval( timer );
        submitQuiz();
    }
}, 1000 );

function submitQuiz ()
{
    let score = 5; // demo score
    fetch( '/submit_quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify( { score: score, subject: "maths" } )
    } )
        .then( res => res.json() )
        .then( data =>
        {
            alert( "XP Earned: " + data.xp );
            window.location = "/dashboard";
        } );
}
