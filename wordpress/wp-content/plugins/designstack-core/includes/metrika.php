<?php
/**
 * Яндекс Метрика: счётчик, цели, сегменты.
 *
 * Меряем работу человека, а не хиты: каждая цель — шаг одного из сценариев
 * brief §4. Список целей и воронок — docs/analytics/goals.md; названия там,
 * в `track.js` и в кабинете Метрики должны совпадать буква в букву.
 *
 * Счётчик выводится только на продакшене. Локально вместо него заглушка:
 * события видно в консоли, а в статистику не попадает наша же отладка.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Идентификатор счётчика. Не секрет: он и так виден в коде страницы.
 *
 * @return string
 */
function designstack_core_metrika_id(): string {
	return trim( (string) get_option( 'designstack_metrika_id', '' ) );
}

/**
 * Продакшен ли это.
 *
 * @return bool
 */
function designstack_core_is_production(): bool {
	return 'production' === wp_get_environment_type();
}

/**
 * Настройки: идентификатор счётчика и коды подтверждения для Вебмастера и Search Console.
 *
 * @return void
 */
function designstack_core_settings(): void {
	foreach ( array( 'designstack_metrika_id', 'designstack_verification_yandex', 'designstack_verification_google' ) as $key ) {
		register_setting(
			'designstack',
			$key,
			array(
				'type'              => 'string',
				'default'           => '',
				'sanitize_callback' => 'sanitize_text_field',
				'show_in_rest'      => false,
			)
		);
	}
}
add_action( 'admin_init', 'designstack_core_settings' );

/**
 * Страница настроек плагина.
 *
 * @return void
 */
function designstack_core_settings_page(): void {
	add_options_page(
		__( 'DesignStack', 'designstack-core' ),
		__( 'DesignStack', 'designstack-core' ),
		'manage_options',
		'designstack',
		'designstack_core_settings_render'
	);
}
add_action( 'admin_menu', 'designstack_core_settings_page' );

/**
 * Разметка страницы настроек.
 *
 * @return void
 */
function designstack_core_settings_render(): void {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}

	$fields = array(
		'designstack_metrika_id'          => __( 'Номер счётчика Яндекс Метрики', 'designstack-core' ),
		'designstack_verification_yandex' => __( 'Код подтверждения Яндекс Вебмастера', 'designstack-core' ),
		'designstack_verification_google' => __( 'Код подтверждения Google Search Console', 'designstack-core' ),
	);

	echo '<div class="wrap"><h1>' . esc_html__( 'DesignStack', 'designstack-core' ) . '</h1>';
	echo '<form method="post" action="options.php">';
	settings_fields( 'designstack' );
	echo '<table class="form-table"><tbody>';

	foreach ( $fields as $key => $label ) {
		printf(
			'<tr><th scope="row"><label for="%1$s">%2$s</label></th>'
			. '<td><input type="text" class="regular-text" id="%1$s" name="%1$s" value="%3$s"></td></tr>',
			esc_attr( $key ),
			esc_html( $label ),
			esc_attr( (string) get_option( $key, '' ) )
		);
	}

	echo '</tbody></table>';
	printf(
		'<p class="description">%s</p>',
		esc_html__( 'Счётчик работает только на продакшене. На локальной машине события пишутся в консоль браузера и в статистику не попадают.', 'designstack-core' )
	);
	submit_button();
	echo '</form></div>';
}

/**
 * Код счётчика или заглушка.
 *
 * Вебвизор выключен намеренно: он пишет экран посетителя целиком, а нам для целей
 * хватает кликов и переходов. Карта кликов оставлена — она нужна для гипотез
 * про первый клик.
 *
 * @return void
 */
function designstack_core_metrika(): void {
	$id = designstack_core_metrika_id();

	if ( ! designstack_core_is_production() || '' === $id ) {
		// Без счётчика track.js всё равно должен работать: иначе локально не проверить,
		// что цель вообще срабатывает и с какими параметрами.
		echo "<script>window.ym=window.ym||function(){console.debug('ym',arguments)};</script>\n";

		return;
	}

	$params = wp_json_encode( designstack_core_page_params(), JSON_UNESCAPED_UNICODE );

	?>
<script>
(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
(window,document,'script','https://mc.yandex.ru/metrika/tag.js','ym');
ym(<?php echo (int) $id; ?>,'init',{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:false,ecommerce:false});
ym(<?php echo (int) $id; ?>,'params',<?php echo $params; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- собрано wp_json_encode. ?>);
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/<?php echo (int) $id; ?>" style="position:absolute;left:-9999px" alt=""></div></noscript>
	<?php
}
add_action( 'wp_head', 'designstack_core_metrika', 2 );

/**
 * Параметры визита: по ним строятся сегменты «кто смотрит закрытые сервисы».
 *
 * @return array<string, mixed>
 */
function designstack_core_page_params(): array {
	$params = array();

	if ( is_singular( 'resource' ) ) {
		$id = get_queried_object_id();

		$params['resource_type'] = designstack_core_get_type( $id );
		$params['ru_open']       = (string) designstack_core_get_field( $id, 'ru_open' );
		$params['ru_payment']    = (string) designstack_core_get_field( $id, 'ru_payment' );
		$params['pricing']       = (string) designstack_core_get_field( $id, 'pricing' );
	} else {
		$term = designstack_core_archive_term();

		if ( $term && 'resource_type' === $term->taxonomy ) {
			$params['resource_type'] = $term->slug;
		}
	}

	return array_filter( $params );
}

/**
 * Скрипт целей.
 *
 * @return void
 */
function designstack_core_track_script(): void {
	$file = DESIGNSTACK_CORE_DIR . 'assets/js/track.js';

	if ( ! file_exists( $file ) ) {
		return;
	}

	wp_enqueue_script(
		'designstack-track',
		DESIGNSTACK_CORE_URL . 'assets/js/track.js',
		array(),
		(string) filemtime( $file ),
		true
	);

	wp_add_inline_script(
		'designstack-track',
		'window.designstackMetrika=' . wp_json_encode(
			array(
				'id'     => designstack_core_is_production() ? (int) designstack_core_metrika_id() : 0,
				'params' => designstack_core_page_params(),
			),
			JSON_UNESCAPED_UNICODE
		) . ';',
		'before'
	);
}
add_action( 'wp_enqueue_scripts', 'designstack_core_track_script' );

/**
 * Атрибуты цели для ссылки на ресурс.
 *
 * Сегменты строятся по ним: «кто уходит на закрытые сервисы», «кто уходит
 * с бесплатных». Значения — те же слаги, что в полях записи.
 *
 * @param int $post_id Идентификатор записи.
 * @return string
 */
function designstack_core_track_attrs( int $post_id ): string {
	$map = array(
		'resource-type' => (string) designstack_core_get_type( $post_id ),
		'slug'          => (string) get_post_field( 'post_name', $post_id ),
		'ru-open'       => (string) designstack_core_get_field( $post_id, 'ru_open' ),
		'ru-payment'    => (string) designstack_core_get_field( $post_id, 'ru_payment' ),
	);

	$out = array();

	foreach ( $map as $key => $value ) {
		if ( '' !== $value ) {
			$out[] = sprintf( 'data-track-%s="%s"', esc_attr( $key ), esc_attr( $value ) );
		}
	}

	return implode( ' ', $out );
}
