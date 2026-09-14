/* Переключатель темы, этап 10: кнопка .ds-theme-toggle ставит data-theme на <html> и запоминает выбор. */
( function () {
	var KEY = 'designstack-theme';
	var root = document.documentElement;
	var media = window.matchMedia( '(prefers-color-scheme: dark)' );

	function isDark() {
		var chosen = root.getAttribute( 'data-theme' );
		return chosen ? chosen === 'dark' : media.matches;
	}

	function sync() {
		var pressed = isDark() ? 'true' : 'false';
		document.querySelectorAll( '.ds-theme-toggle' ).forEach( function ( button ) {
			button.setAttribute( 'aria-pressed', pressed );
		} );
	}

	document.addEventListener( 'click', function ( event ) {
		var button = event.target.closest( '.ds-theme-toggle' );
		var next;
		if ( ! button ) {
			return;
		}
		next = isDark() ? 'light' : 'dark';
		root.setAttribute( 'data-theme', next );
		try {
			window.localStorage.setItem( KEY, next );
		} catch ( error ) {
			// Хранилище закрыто: тема действует до перезагрузки.
		}
		sync();

		// Цель theme_toggle: значение известно только здесь — после клика
		// кнопка уже показывает следующее состояние, а не выбранное.
		if ( window.designstackTrack ) {
			window.designstackTrack( 'theme_toggle', { to: next } );
		}
	} );

	media.addEventListener( 'change', sync );
	sync();
}() );
