( function () {
	var toggle = document.querySelector( '.sg-highlight' );

	if ( ! toggle ) {
		return;
	}

	toggle.addEventListener( 'click', function () {
		var on = document.body.classList.toggle( 'is-highlight-interactive' );
		toggle.setAttribute( 'aria-pressed', String( on ) );
	} );
}() );
