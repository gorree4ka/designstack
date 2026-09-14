( function () {
	var menu = document.querySelector( '.ds-header__menu' );
	var search = document.querySelector( '.ds-header__search-menu' );
	var header = document.querySelector( '.ds-header' );

	// Со скриптом меню и поиск сворачиваются в выпадающие панели; без него они остаются
	// раскрытыми в потоке страницы и ничего собой не накрывают (этап 14).
	if ( header ) {
		header.classList.add( 'ds-header--js' );
	}

	function follow( element, query ) {
		if ( ! element ) {
			return;
		}

		var media = window.matchMedia( query );
		var sync = function () {
			element.open = ! media.matches;
		};

		media.addEventListener( 'change', sync );
		sync();
	}

	// Без скрипта меню и поиск остаются раскрытыми: навигация работает и без JavaScript.
	follow( menu, '(max-width: 899px)' );
	follow( search, '(max-width: 1199px)' );

	// Открытая панель закрывает соседнюю: они занимают одно место под шапкой.
	[ [ menu, search ], [ search, menu ] ].forEach( function ( pair ) {
		if ( ! pair[ 0 ] || ! pair[ 1 ] ) {
			return;
		}

		pair[ 0 ].addEventListener( 'toggle', function () {
			if ( pair[ 0 ].open ) {
				pair[ 1 ].open = false;
			}
		} );
	} );
}() );
