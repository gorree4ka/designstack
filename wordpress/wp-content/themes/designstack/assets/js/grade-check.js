/**
 * Проверка грейда: пошаговый проход и подсчёт результата.
 *
 * Без скрипта страница показывает все вопросы списком и остаётся читаемой. Скрипт превращает
 * список в проверку по одному вопросу, считает профиль и собирает план из ссылок, которые
 * сервер уже положил рядом с каждым вопросом.
 *
 * Ответы живут в localStorage: регистрации на сайте нет (D18), а бросить проверку на середине
 * и вернуться — обычное дело.
 */
( function () {
	'use strict';

	var root = document.querySelector( '[data-check]' );

	if ( ! root ) {
		return;
	}

	var KEY = 'designstack-grade-check';
	var ORDER = [ 'junior', 'middle', 'senior' ];
	var NAMES = { junior: 'Junior', middle: 'Middle', senior: 'Senior' };
	var SHARE = 0.7;

	var items = Array.prototype.slice.call( root.querySelectorAll( '[data-check-q]' ) );
	var intro = root.querySelector( '[data-check-intro]' );
	var flow = root.querySelector( '[data-check-flow]' );
	var bar = root.querySelector( '[data-check-bar]' );
	var fill = root.querySelector( '[data-check-fill]' );
	var result = root.querySelector( '[data-check-result]' );
	var total = items.length;
	var at = 0;

	root.classList.add( 'is-stepped' );

	function answerOf( item ) {
		return item.querySelector( 'input:checked' );
	}

	function read() {
		try {
			var kept = JSON.parse( localStorage.getItem( KEY ) || 'null' );

			if ( ! kept ) {
				return false;
			}

			var any = false;

			items.forEach( function ( item ) {
				var value = kept[ item.getAttribute( 'data-skill' ) ];

				if ( typeof value !== 'number' ) {
					return;
				}

				var input = item.querySelectorAll( 'input' )[ value ];

				if ( input ) {
					input.checked = true;
					any = true;
				}
			} );

			return any;
		} catch ( e ) {
			return false;
		}
	}

	function write() {
		try {
			var kept = {};

			items.forEach( function ( item ) {
				var input = answerOf( item );

				if ( input ) {
					kept[ item.getAttribute( 'data-skill' ) ] = Number( input.value );
				}
			} );

			localStorage.setItem( KEY, JSON.stringify( kept ) );
		} catch ( e ) {
			/* приватное окно или запрет на хранилище: проверка работает, просто не запомнится */
		}
	}

	function show( index, focus ) {
		at = Math.max( 0, Math.min( index, total - 1 ) );

		items.forEach( function ( item, i ) {
			item.hidden = i !== at;
		} );

		var item = items[ at ];
		var next = item.querySelector( '[data-check-next]' );
		var back = item.querySelector( '[data-check-back]' );

		next.disabled = ! answerOf( item );
		next.textContent = at === total - 1 ? 'Показать результат' : 'Дальше';
		back.hidden = at === 0;
		fill.style.width = Math.round( ( at / total ) * 100 ) + '%';
		bar.setAttribute( 'aria-valuenow', String( at + 1 ) );

		if ( focus ) {
			var legend = item.querySelector( '[data-check-step]' );

			if ( legend ) {
				legend.setAttribute( 'tabindex', '-1' );
				legend.focus();
			}
		}
	}

	function ranks() {
		return items.map( function ( item ) {
			var input = answerOf( item );
			var grade = input ? input.getAttribute( 'data-grade' ) : '';

			return grade ? ORDER.indexOf( grade ) + 1 : 0;
		} );
	}

	function node( tag, className, text ) {
		var el = document.createElement( tag );

		if ( className ) {
			el.className = className;
		}

		if ( text ) {
			el.textContent = text;
		}

		return el;
	}

	function svgNode( tag, className ) {
		var el = document.createElementNS( 'http://www.w3.org/2000/svg', tag );

		if ( className ) {
			el.setAttribute( 'class', className );
		}

		return el;
	}

	/**
	 * Точка на оси диаграммы. Углы считаются от верха по часовой стрелке, центр — 160,160
	 * в системе координат 320×320: `viewBox` держит пропорции, размер задаёт CSS.
	 */
	function point( i, count, radius ) {
		var angle = ( ( Math.PI * 2 * i ) / count ) - ( Math.PI / 2 );

		return {
			x: ( 160 + ( Math.cos( angle ) * radius ) ).toFixed( 1 ),
			y: ( 160 + ( Math.sin( angle ) * radius ) ).toFixed( 1 )
		};
	}

	function polygon( className, count, at ) {
		var el = svgNode( 'polygon', className );
		var pts = [];

		for ( var i = 0; i < count; i++ ) {
			var p = point( i, count, at( i ) );
			pts.push( p.x + ',' + p.y );
		}

		el.setAttribute( 'points', pts.join( ' ' ) );

		return el;
	}

	/**
	 * Лепестковая диаграмма профиля. Оси подписаны номерами, а не названиями: тринадцать
	 * названий по кругу не помещаются даже на широком экране, а на телефоне становятся
	 * нечитаемыми. Расшифровка — в списке под диаграммой, номера там те же.
	 */
	function radar( list ) {
		var count = list.length;
		var box = svgNode( 'svg', 'ds-check__radar' );

		box.setAttribute( 'viewBox', '0 0 320 320' );
		// Диаграмма ничего не добавляет к списку ниже, поэтому для чтеца она декоративна.
		box.setAttribute( 'aria-hidden', 'true' );

		[ 40, 80, 120 ].forEach( function ( r ) {
			box.appendChild( polygon( 'ds-check__radar-ring', count, function () {
				return r;
			} ) );
		} );

		list.forEach( function ( area, i ) {
			var p = point( i, count, 120 );
			var axis = svgNode( 'line', 'ds-check__radar-axis' );

			axis.setAttribute( 'x1', 160 );
			axis.setAttribute( 'y1', 160 );
			axis.setAttribute( 'x2', p.x );
			axis.setAttribute( 'y2', p.y );
			box.appendChild( axis );
		} );

		// Пустая область не схлопывается в точку: иначе форма врёт, что данных нет вовсе.
		function reach( i ) {
			return Math.max( list[ i ].share, 0.04 ) * 120;
		}

		box.appendChild( polygon( 'ds-check__radar-shape', count, reach ) );

		list.forEach( function ( area, i ) {
			var p = point( i, count, reach( i ) );
			var dot = svgNode( 'circle', 'ds-check__radar-dot' );

			dot.setAttribute( 'cx', p.x );
			dot.setAttribute( 'cy', p.y );
			dot.setAttribute( 'r', 4 );
			box.appendChild( dot );

			var out = point( i, count, 142 );
			var num = svgNode( 'text', 'ds-check__radar-num' );

			num.setAttribute( 'x', out.x );
			num.setAttribute( 'y', out.y );
			num.setAttribute( 'text-anchor', 'middle' );
			num.setAttribute( 'dominant-baseline', 'central' );
			num.textContent = area.num;
			box.appendChild( num );
		} );

		return box;
	}

	function rowsOf( list ) {
		var rows = node( 'ul', 'ds-check__rows' );

		list.forEach( function ( area ) {
			var level = Math.floor( area.share * ORDER.length );
			var row = node( 'li', 'ds-check__row' );
			var name = node( 'span', 'ds-check__row-name' );

			name.appendChild( node( 'span', 'ds-check__row-num', String( area.num ) ) );
			name.appendChild( document.createTextNode( area.name ) );
			row.appendChild( name );

			var track = node( 'span', 'ds-check__track' );
			var line = node( 'span', 'ds-check__track-fill' );

			line.style.width = Math.round( area.share * 100 ) + '%';
			track.appendChild( line );
			row.appendChild( track );

			row.appendChild( node( 'span', 'ds-check__row-grade', level ? NAMES[ ORDER[ level - 1 ] ] : 'нет ступени' ) );
			rows.appendChild( row );
		} );

		return rows;
	}

	function group( title, list ) {
		var box = node( 'div', 'ds-check__group' );

		box.appendChild( node( 'h3', 'ds-check__group-title', title ) );
		box.appendChild( rowsOf( list ) );

		return box;
	}

	function render() {
		var list = ranks();
		var counts = [ 0, 0, 0 ];

		list.forEach( function ( rank ) {
			for ( var i = 0; i < rank; i++ ) {
				counts[ i ]++;
			}
		} );

		var need = Math.ceil( total * SHARE );
		var reached = '';

		for ( var i = ORDER.length - 1; i >= 0; i-- ) {
			if ( counts[ i ] >= need ) {
				reached = ORDER[ i ];
				break;
			}
		}

		result.textContent = '';

		var head = node( 'div', 'ds-check__verdict' );
		head.appendChild( node( 'p', 'ds-check__verdict-label', 'Ориентир по нашей карте' ) );
		head.appendChild( node( 'p', 'ds-check__verdict-value', reached ? NAMES[ reached ] : 'Ниже Junior' ) );
		head.appendChild( node( 'p', 'ds-check__verdict-why', reached
			? 'Junior взят в ' + counts[ 0 ] + ' навыках, Middle в ' + counts[ 1 ] + ', Senior в ' + counts[ 2 ]
				+ ' — из ' + total + '. Ориентир ставится по ступени, взятой не меньше чем в ' + need + ' навыках.'
			: 'До порога в ' + need + ' навыков не хватило: Junior взят в ' + counts[ 0 ] + '. Это не приговор, а точка, с которой видно, куда идти.' ) );
		result.appendChild( head );

		// профиль по областям: считаем среднюю ступень внутри каждой
		var areas = [];
		var byArea = {};

		items.forEach( function ( item, i ) {
			var name = item.querySelector( '.ds-check__area' ).textContent;

			if ( ! byArea[ name ] ) {
				byArea[ name ] = { name: name, sum: 0, n: 0 };
				areas.push( byArea[ name ] );
			}

			byArea[ name ].sum += list[ i ];
			byArea[ name ].n++;
		} );

		result.appendChild( node( 'h2', 'ds-check__subtitle', 'Профиль по областям' ) );

		// Номер области — её место в карте: он же подписывает ось диаграммы.
		var ranked = areas.map( function ( area, i ) {
			return { name: area.name, num: i + 1, share: area.sum / area.n / ORDER.length };
		} );

		var figure = node( 'figure', 'ds-check__figure' );

		figure.appendChild( radar( ranked ) );
		figure.appendChild( node( 'figcaption', 'ds-check__radar-key',
			'Кольца — ступени: внутреннее Junior, среднее Middle, внешнее Senior. Номера осей совпадают с номерами в списке.' ) );
		result.appendChild( figure );

		var sorted = ranked.slice().sort( function ( a, b ) {
			return b.share - a.share;
		} );

		// Делить профиль на сильное и слабое имеет смысл, только если области правда расходятся.
		var spread = sorted[ 0 ].share - sorted[ sorted.length - 1 ].share;

		if ( sorted.length < 7 || spread < 0.01 ) {
			result.appendChild( node( 'p', 'ds-check__plan-none',
				'Профиль ровный: области идут вровень, и выделять среди них сильные и слабые не по чему.' ) );
			result.appendChild( rowsOf( sorted ) );
		} else {
			result.appendChild( group( 'Сильные стороны', sorted.slice( 0, 3 ) ) );
			result.appendChild( group( 'Остальные области', sorted.slice( 3, -3 ) ) );
			result.appendChild( group( 'Зона роста', sorted.slice( -3 ) ) );
		}

		// план: навыки ниже ориентира, с материалами каталога
		var target = reached ? ORDER.indexOf( reached ) + 1 : 1;
		var weak = items
			.map( function ( item, i ) {
				return { item: item, rank: list[ i ] };
			} )
			.filter( function ( x ) {
				return x.rank < target;
			} )
			.sort( function ( a, b ) {
				return a.rank - b.rank;
			} )
			.slice( 0, 8 );

		result.appendChild( node( 'h2', 'ds-check__subtitle', 'С чего расти дальше' ) );

		if ( ! weak.length ) {
			result.appendChild( node( 'p', 'ds-check__plan-none',
				'Навыков ниже ориентира нет: профиль ровный. Тогда план строится от следующей ступени — посмотрите области, где полоска короче остальных.' ) );
		} else {
			var plan = node( 'ul', 'ds-check__plan' );

			weak.forEach( function ( x ) {
				var li = node( 'li', 'ds-check__plan-item' );
				li.appendChild( node( 'h3', 'ds-check__plan-name', x.item.querySelector( '.ds-check__name' ).textContent ) );
				li.appendChild( node( 'p', 'ds-check__plan-area', x.item.querySelector( '.ds-check__area' ).textContent ) );

				var links = x.item.querySelector( '[data-check-links]' ).cloneNode( true );
				links.hidden = false;
				links.removeAttribute( 'data-check-links' );
				li.appendChild( links );
				plan.appendChild( li );
			} );

			result.appendChild( plan );
		}

		// Полная карта — отдельная страница: туда возвращаются месяцами, сюда заходят раз (D152).
		var mapUrl = root.getAttribute( 'data-map-url' );

		if ( mapUrl ) {
			var mapBox = node( 'div', 'ds-check__map' );

			mapBox.appendChild( node( 'p', 'ds-check__map-text',
				'Это ближайшие шаги. Вся карта — 37 навыков по три ступени у каждого — живёт отдельной страницей: там видно, где вы сейчас и что открыто дальше.' ) );

			var mapLink = node( 'a', 'ds-button ds-button--primary', 'Открыть карту развития' );

			mapLink.href = mapUrl;
			mapBox.appendChild( mapLink );
			result.appendChild( mapBox );
		}

		var again = node( 'button', 'ds-button ds-button--secondary', 'Пройти заново' );
		again.type = 'button';
		again.addEventListener( 'click', function () {
			items.forEach( function ( item ) {
				var checked = answerOf( item );

				if ( checked ) {
					checked.checked = false;
				}
			} );

			write();
			result.hidden = true;
			flow.hidden = false;
			show( 0, true );
		} );

		result.appendChild( node( 'div', 'ds-check__actions' ) ).appendChild( again );

		flow.hidden = true;
		result.hidden = false;
		result.focus();
	}

	function start() {
		intro.hidden = true;
		flow.hidden = false;
		bar.hidden = false;

		var first = -1;

		items.some( function ( item, i ) {
			if ( ! answerOf( item ) ) {
				first = i;

				return true;
			}

			return false;
		} );

		// Отвечено всё — человеку нужен результат, а не первый вопрос заново.
		// Пройти проверку ещё раз можно кнопкой на самом результате.
		if ( first < 0 ) {
			render();

			return;
		}

		show( first, true );
	}

	items.forEach( function ( item, i ) {
		item.hidden = true;
		item.querySelector( '[data-check-nav]' ).hidden = false;

		item.addEventListener( 'change', function () {
			write();
			item.querySelector( '[data-check-next]' ).disabled = ! answerOf( item );
		} );

		item.querySelector( '[data-check-next]' ).addEventListener( 'click', function () {
			if ( i === total - 1 ) {
				render();

				return;
			}

			show( i + 1, true );
		} );

		item.querySelector( '[data-check-back]' ).addEventListener( 'click', function () {
			show( i - 1, true );
		} );
	} );

	flow.hidden = true;

	if ( read() ) {
		var resume = root.querySelector( '[data-check-resume]' );
		var whole = items.every( answerOf );

		// Подпись и кнопка говорят правду о состоянии: продолжить незаконченное —
		// это не то же самое, что посмотреть готовый результат.
		resume.textContent = whole
			? 'Проверка пройдена — откроется ваш результат'
			: 'Есть незаконченная попытка — продолжите с того же места';
		resume.hidden = false;

		if ( whole ) {
			root.querySelector( '[data-check-start]' ).textContent = 'Посмотреть результат';
		}
	}

	root.querySelector( '[data-check-start]' ).addEventListener( 'click', start );
} )();
