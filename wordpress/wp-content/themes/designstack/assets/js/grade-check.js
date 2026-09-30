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
	 * Точка на оси диаграммы. Углы считаются от верха по часовой стрелке, центр — 0,0,
	 * внешнее кольцо — радиус 120. `viewBox` собирается по рамке рисунка вместе с подписями
	 * (fitRadar), размер на экране задаёт CSS.
	 */
	function angle( i, count ) {
		return ( ( Math.PI * 2 * i ) / count ) - ( Math.PI / 2 );
	}

	function point( i, count, radius ) {
		var a = angle( i, count );

		return {
			x: ( Math.cos( a ) * radius ).toFixed( 1 ),
			y: ( Math.sin( a ) * radius ).toFixed( 1 )
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

	var RADIUS = 120;
	var LABEL_GAP = 12;

	function levelOf( share ) {
		return Math.floor( share * ORDER.length );
	}

	/**
	 * Лепестковая диаграмма профиля. У конца каждой оси — короткое название области и ступень
	 * в ней (D192): круг отвечает на вопрос «где я силён» без сверки со списком. Полные названия —
	 * в списке под диаграммой. Заливка — градиент от центра к кольцу Senior: он привязан к кругу,
	 * а не к фигуре, поэтому чем дальше область дотянулась к краю, тем гуще там цвет.
	 */
	function radar( list ) {
		var count = list.length;
		var box = svgNode( 'svg', 'ds-check__radar' );
		var defs = svgNode( 'defs' );
		var art = svgNode( 'g' );

		box.setAttribute( 'viewBox', '-200 -200 400 400' );
		// Диаграмма ничего не добавляет к списку ниже, поэтому для чтеца она декоративна.
		box.setAttribute( 'aria-hidden', 'true' );
		box.appendChild( defs );
		box.appendChild( art );

		var fill = svgNode( 'radialGradient' );

		fill.setAttribute( 'id', 'ds-check-radar-fill' );
		fill.setAttribute( 'gradientUnits', 'userSpaceOnUse' );
		fill.setAttribute( 'cx', 0 );
		fill.setAttribute( 'cy', 0 );
		fill.setAttribute( 'r', RADIUS );
		[ 'in', 'out' ].forEach( function ( at, i ) {
			var stop = svgNode( 'stop', 'ds-check__radar-stop-' + at );

			stop.setAttribute( 'offset', i );
			fill.appendChild( stop );
		} );
		defs.appendChild( fill );

		[ 40, 80, 120 ].forEach( function ( r ) {
			art.appendChild( polygon( 'ds-check__radar-ring', count, function () {
				return r;
			} ) );
		} );

		list.forEach( function ( area, i ) {
			var p = point( i, count, RADIUS );
			var axis = svgNode( 'line', 'ds-check__radar-axis' );

			axis.setAttribute( 'x1', 0 );
			axis.setAttribute( 'y1', 0 );
			axis.setAttribute( 'x2', p.x );
			axis.setAttribute( 'y2', p.y );
			art.appendChild( axis );
		} );

		// Пустая область не схлопывается в точку: иначе форма врёт, что данных нет вовсе.
		function reach( i ) {
			return Math.max( list[ i ].share, 0.04 ) * RADIUS;
		}

		var shape = polygon( 'ds-check__radar-shape', count, reach );

		// Через style, а не атрибут: правило из CSS перебило бы атрибут fill.
		shape.style.fill = 'url(#ds-check-radar-fill)';
		art.appendChild( shape );

		list.forEach( function ( area, i ) {
			var p = point( i, count, reach( i ) );
			var dot = svgNode( 'circle', 'ds-check__radar-dot' );

			dot.setAttribute( 'cx', p.x );
			dot.setAttribute( 'cy', p.y );
			dot.setAttribute( 'r', 4 );
			art.appendChild( dot );
		} );

		list.forEach( function ( area, i ) {
			var level = levelOf( area.share );
			var label = svgNode( 'text', 'ds-check__radar-label' );
			var name = svgNode( 'tspan', 'ds-check__radar-name' );
			var grade = svgNode( 'tspan', 'ds-check__radar-grade' + ( level ? ' is-on' : '' ) );

			label.setAttribute( 'text-anchor', 'middle' );
			label.setAttribute( 'data-axis', i );
			name.setAttribute( 'x', 0 );
			name.textContent = area.short || area.name;
			grade.setAttribute( 'x', 0 );
			grade.setAttribute( 'dy', '1.3em' );
			grade.textContent = level ? NAMES[ ORDER[ level - 1 ] ] : 'нет ступени';
			label.appendChild( name );
			label.appendChild( grade );
			art.appendChild( label );
		} );

		return box;
	}

	/**
	 * Раскладка подписей по уже нарисованному тексту: размер строки знает только браузер.
	 * Подпись встаёт снаружи конца оси: центр её рамки сдвинут от точки по направлению оси на
	 * полвысоты вверх или вниз и на полширины вбок. Вбок сдвиг растёт быстрее косинуса, поэтому
	 * подписи у низа и верха круга расходятся каждая в свою сторону. Если соседние подписи всё же
	 * слиплись — на телефоне кегль крупнее, — та, что ближе к вертикали, отходит от круга вверх
	 * или вниз, пока между ними не появится зазор. Потом рамка всего рисунка становится viewBox:
	 * подпись не обрезается ни на какой ширине. Работает только на видимом рисунке — у скрытого
	 * рамка нулевая.
	 */
	function fitRadar( box ) {
		var art = box.lastChild;
		var labels = Array.prototype.slice.call( box.querySelectorAll( '.ds-check__radar-label' ) );
		var count = labels.length;
		var room = 3;

		var spots = labels.map( function ( label ) {
			label.removeAttribute( 'transform' );

			var b = label.getBBox();
			var a = angle( Number( label.getAttribute( 'data-axis' ) ), count );
			var side = Math.max( -1, Math.min( 1, Math.cos( a ) * 2.5 ) );
			var cx = ( Math.cos( a ) * ( RADIUS + LABEL_GAP ) ) + ( side * b.width / 2 );
			var cy = ( Math.sin( a ) * ( RADIUS + LABEL_GAP ) ) + ( Math.sin( a ) * b.height / 2 );

			return { a: a, b: b, x: cx - b.x - ( b.width / 2 ), y: cy - b.y - ( b.height / 2 ) };
		} );

		function clash( p, q ) {
			return p.b.x + p.x < q.b.x + q.x + q.b.width + room && q.b.x + q.x < p.b.x + p.x + p.b.width + room &&
				p.b.y + p.y < q.b.y + q.y + q.b.height + room && q.b.y + q.y < p.b.y + p.y + p.b.height + room;
		}

		for ( var round = 0; round < 40; round++ ) {
			var moved = false;

			for ( var i = 0; i < count; i++ ) {
				var p = spots[ i ];
				var q = spots[ ( i + 1 ) % count ];

				if ( clash( p, q ) ) {
					var step = Math.abs( Math.cos( p.a ) ) < Math.abs( Math.cos( q.a ) ) ? p : q;

					step.y += Math.sin( step.a ) < 0 ? -2 : 2;
					moved = true;
				}
			}

			if ( ! moved ) {
				break;
			}
		}

		spots.forEach( function ( spot, i ) {
			labels[ i ].setAttribute( 'transform', 'translate(' + spot.x.toFixed( 1 ) + ' ' + spot.y.toFixed( 1 ) + ')' );
		} );

		var frame = art.getBBox();

		if ( ! frame.width ) {
			return;
		}

		box.setAttribute( 'viewBox', [ frame.x - 4, frame.y - 4, frame.width + 8, frame.height + 8 ].map( function ( v ) {
			return v.toFixed( 1 );
		} ).join( ' ' ) );
	}

	// Кегль подписей зависит от ширины рисунка (@container в patterns.css), поэтому при смене
	// ширины подписи раскладываются заново.
	var radarWatch = null;

	function watchRadar( figure, box ) {
		var width = 0;

		if ( radarWatch ) {
			radarWatch.disconnect();
			radarWatch = null;
		}

		fitRadar( box );

		if ( document.fonts && document.fonts.ready ) {
			document.fonts.ready.then( function () {
				fitRadar( box );
			} );
		}

		if ( window.ResizeObserver ) {
			radarWatch = new ResizeObserver( function () {
				if ( figure.clientWidth !== width ) {
					width = figure.clientWidth;
					fitRadar( box );
				}
			} );
			radarWatch.observe( figure );
		}
	}

	function rowsOf( list ) {
		var rows = node( 'ul', 'ds-check__rows' );

		list.forEach( function ( area ) {
			var level = levelOf( area.share );
			var row = node( 'li', 'ds-check__row' );

			row.appendChild( node( 'span', 'ds-check__row-name', area.name ) );

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

		// Карта — следующий шаг после ориентира, поэтому кнопка стоит в его карточке, на первом
		// экране результата. Внизу, после плана, она повторяется для дочитавших (D192).
		var mapUrl = root.getAttribute( 'data-map-url' );

		if ( mapUrl ) {
			var headAction = node( 'div', 'ds-check__verdict-action' );
			var headLink = node( 'a', 'ds-button ds-button--primary', 'Открыть карту развития' );

			headLink.href = mapUrl;
			headAction.appendChild( headLink );
			head.appendChild( headAction );
		}

		result.appendChild( head );

		// профиль по областям: считаем среднюю ступень внутри каждой
		var areas = [];
		var byArea = {};

		items.forEach( function ( item, i ) {
			var tag = item.querySelector( '.ds-check__area' );
			var name = tag.textContent;

			if ( ! byArea[ name ] ) {
				byArea[ name ] = { name: name, short: tag.getAttribute( 'data-short' ) || '', sum: 0, n: 0 };
				areas.push( byArea[ name ] );
			}

			byArea[ name ].sum += list[ i ];
			byArea[ name ].n++;
		} );

		result.appendChild( node( 'h2', 'ds-check__subtitle', 'Профиль по областям' ) );

		// Оси идут в порядке карты, список ниже — от сильной области к слабой.
		var ranked = areas.map( function ( area ) {
			return { name: area.name, short: area.short, share: area.sum / area.n / ORDER.length };
		} );

		var figure = node( 'figure', 'ds-check__figure' );
		var chart = radar( ranked );

		figure.appendChild( chart );
		figure.appendChild( node( 'figcaption', 'ds-check__radar-key',
			'Кольца — ступени: внутреннее Junior, среднее Middle, внешнее Senior. Чем ближе к краю, тем гуще цвет.' ) );
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
		again.addEventListener( 'click', restart );

		result.appendChild( node( 'div', 'ds-check__actions' ) ).appendChild( again );

		flow.hidden = true;
		result.hidden = false;
		// Подписи раскладываются по размеру текста, а он известен только у видимого рисунка.
		watchRadar( figure, chart );
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

	/**
	 * Проверка с первого вопроса. Отметки снимаются только на странице: в хранилище старые
	 * ответы остаются, пока не отмечен первый новый. Передумал и ушёл — результат цел.
	 */
	function restart() {
		items.forEach( function ( item ) {
			var checked = answerOf( item );

			if ( checked ) {
				checked.checked = false;
			}
		} );

		intro.hidden = true;
		result.hidden = true;
		flow.hidden = false;
		bar.hidden = false;
		show( 0, true );
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

	var kept = read();

	if ( kept ) {
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
			root.querySelector( '[data-check-restart]' ).hidden = false;
		}
	}

	root.querySelector( '[data-check-start]' ).addEventListener( 'click', start );
	root.querySelector( '[data-check-restart]' ).addEventListener( 'click', restart );

	// «Пройти проверку заново» с главной и с карты ведёт сюда с #again: человек уже выбрал
	// начать сначала, и вступление с «Посмотреть результат» его бы только остановило.
	// Пометка ловится и без перезагрузки: ссылка с #again может вести на эту же страницу.
	function fromLink() {
		if ( '#again' !== window.location.hash ) {
			return;
		}

		if ( window.history && window.history.replaceState ) {
			window.history.replaceState( null, '', window.location.pathname + window.location.search );
		}

		if ( kept ) {
			restart();
		}
	}

	fromLink();
	window.addEventListener( 'hashchange', fromLink );
} )();
