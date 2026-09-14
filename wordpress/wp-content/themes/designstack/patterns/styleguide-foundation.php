<?php
/**
 * Title: Витрина: фундамент
 * Slug: designstack/styleguide-foundation
 * Categories: designstack-styleguide
 * Inserter: no
 *
 * Списки читаются из theme.json через wp_get_global_settings(): на витрине не может оказаться значения, которого
 * нет в теме. Образцы раскрашены пресет-классами WordPress и классами витрины, поэтому в файле нет собранных
 * на лету имён переменных — их не проверить check_tokens.py.
 *
 * @package designstack
 */

$ds_settings = wp_get_global_settings();
$ds_palette  = isset( $ds_settings['color']['palette']['theme'] ) ? $ds_settings['color']['palette']['theme'] : array();
$ds_fonts    = isset( $ds_settings['typography']['fontSizes']['theme'] ) ? $ds_settings['typography']['fontSizes']['theme'] : array();
$ds_spacing  = isset( $ds_settings['spacing']['spacingSizes']['theme'] ) ? $ds_settings['spacing']['spacingSizes']['theme'] : array();
$ds_radius   = isset( $ds_settings['custom']['radius'] ) ? $ds_settings['custom']['radius'] : array();
$ds_sizes    = isset( $ds_settings['custom']['size'] ) ? $ds_settings['custom']['size'] : array();

$ds_pairs = function ( $values ) {
	$out = array();
	foreach ( $values as $name => $value ) {
		$out[] = $name . ' ' . $value;
	}

	return implode( ' · ', $out );
};

?>
<!-- wp:html -->
<section class="sg-section" id="sg-foundation">
	<h2 class="sg-section__title">Фундамент</h2>
	<p class="sg-section__note">Списки ниже прочитаны из theme.json на этой странице. Цвета показаны в текущей теме: переключи тему в шапке — свотчи станут тёмными.</p>

	<div class="sg-item">
		<h3 class="sg-item__title">color · <?php echo esc_html( (string) count( $ds_palette ) ); ?> семантических токена</h3>
		<div class="sg-swatches">
			<?php foreach ( $ds_palette as $ds_color ) : ?>
			<span class="sg-swatch"><span class="sg-swatch__chip has-background has-<?php echo esc_attr( $ds_color['slug'] ); ?>-background-color"></span><span class="sg-swatch__name ds-meta"><?php echo esc_html( $ds_color['slug'] ); ?></span></span>
			<?php endforeach; ?>
		</div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">font-size · <?php echo esc_html( (string) count( $ds_fonts ) ); ?> кеглей</h3>
		<div class="sg-scale">
			<?php foreach ( $ds_fonts as $ds_font ) : ?>
			<p class="sg-type has-<?php echo esc_attr( _wp_to_kebab_case( $ds_font['slug'] ) ); ?>-font-size">Съешь ещё этих мягких булок <span class="ds-meta"><?php echo esc_html( $ds_font['slug'] . ' · ' . $ds_font['size'] ); ?></span></p>
			<?php endforeach; ?>
		</div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">spacing · шаг 8</h3>
		<div class="sg-scale">
			<?php foreach ( $ds_spacing as $ds_space ) : ?>
			<span class="sg-bar"><span class="sg-bar__fill sg-bar--<?php echo esc_attr( $ds_space['slug'] ); ?>"></span><span class="ds-meta"><?php echo esc_html( $ds_space['name'] . ' · ' . $ds_space['size'] ); ?></span></span>
			<?php endforeach; ?>
		</div>
	</div>

	<div class="sg-item">
		<h3 class="sg-item__title">radius, size, shadow</h3>
		<div class="sg-matrix">
			<div class="sg-cell">
				<p class="sg-cell__label">радиусы</p>
				<div class="sg-cell__body ds-row">
					<span class="ds-logo sg-radius--none" aria-hidden="true"></span>
					<span class="ds-logo sg-radius--xs" aria-hidden="true"></span>
					<span class="ds-logo sg-radius--sm" aria-hidden="true"></span>
					<span class="ds-logo sg-radius--md" aria-hidden="true"></span>
					<span class="ds-logo sg-radius--full" aria-hidden="true"></span>
				</div>
				<p class="ds-meta"><?php echo esc_html( $ds_pairs( $ds_radius ) ); ?></p>
			</div>
			<div class="sg-cell">
				<p class="sg-cell__label">размеры компонентов</p>
				<p class="ds-meta"><?php echo esc_html( $ds_pairs( $ds_sizes ) ); ?></p>
			</div>
			<div class="sg-cell">
				<p class="sg-cell__label">тень — только у выезжающей панели</p>
				<div class="sg-cell__body"><span class="ds-logo ds-logo--lg sg-shadow" aria-hidden="true"></span></div>
			</div>
		</div>
	</div>
</section>
<!-- /wp:html -->
