// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'disponibilidad_slot.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$DisponibilidadSlot {

 String get horaInicio; String get horaFin; EstadoSlot get estado;
/// Create a copy of DisponibilidadSlot
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DisponibilidadSlotCopyWith<DisponibilidadSlot> get copyWith => _$DisponibilidadSlotCopyWithImpl<DisponibilidadSlot>(this as DisponibilidadSlot, _$identity);

  /// Serializes this DisponibilidadSlot to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DisponibilidadSlot&&(identical(other.horaInicio, horaInicio) || other.horaInicio == horaInicio)&&(identical(other.horaFin, horaFin) || other.horaFin == horaFin)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,horaInicio,horaFin,estado);

@override
String toString() {
  return 'DisponibilidadSlot(horaInicio: $horaInicio, horaFin: $horaFin, estado: $estado)';
}


}

/// @nodoc
abstract mixin class $DisponibilidadSlotCopyWith<$Res>  {
  factory $DisponibilidadSlotCopyWith(DisponibilidadSlot value, $Res Function(DisponibilidadSlot) _then) = _$DisponibilidadSlotCopyWithImpl;
@useResult
$Res call({
 String horaInicio, String horaFin, EstadoSlot estado
});




}
/// @nodoc
class _$DisponibilidadSlotCopyWithImpl<$Res>
    implements $DisponibilidadSlotCopyWith<$Res> {
  _$DisponibilidadSlotCopyWithImpl(this._self, this._then);

  final DisponibilidadSlot _self;
  final $Res Function(DisponibilidadSlot) _then;

/// Create a copy of DisponibilidadSlot
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? horaInicio = null,Object? horaFin = null,Object? estado = null,}) {
  return _then(DisponibilidadSlot(
horaInicio: null == horaInicio ? _self.horaInicio : horaInicio // ignore: cast_nullable_to_non_nullable
as String,horaFin: null == horaFin ? _self.horaFin : horaFin // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoSlot,
  ));
}

}


/// Adds pattern-matching-related methods to [DisponibilidadSlot].
extension DisponibilidadSlotPatterns on DisponibilidadSlot {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DisponibilidadSlot value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DisponibilidadSlot() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DisponibilidadSlot value)  $default,){
final _that = this;
switch (_that) {
case _DisponibilidadSlot():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DisponibilidadSlot value)?  $default,){
final _that = this;
switch (_that) {
case _DisponibilidadSlot() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String horaInicio,  String horaFin,  EstadoSlot estado)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DisponibilidadSlot() when $default != null:
return $default(_that.horaInicio,_that.horaFin,_that.estado);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String horaInicio,  String horaFin,  EstadoSlot estado)  $default,) {final _that = this;
switch (_that) {
case _DisponibilidadSlot():
return $default(_that.horaInicio,_that.horaFin,_that.estado);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String horaInicio,  String horaFin,  EstadoSlot estado)?  $default,) {final _that = this;
switch (_that) {
case _DisponibilidadSlot() when $default != null:
return $default(_that.horaInicio,_that.horaFin,_that.estado);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _DisponibilidadSlot implements DisponibilidadSlot {
  const _DisponibilidadSlot({required this.horaInicio, required this.horaFin, required this.estado});
  factory _DisponibilidadSlot.fromJson(Map<String, dynamic> json) => _$DisponibilidadSlotFromJson(json);

@override final  String horaInicio;
@override final  String horaFin;
@override final  EstadoSlot estado;

/// Create a copy of DisponibilidadSlot
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DisponibilidadSlotCopyWith<_DisponibilidadSlot> get copyWith => __$DisponibilidadSlotCopyWithImpl<_DisponibilidadSlot>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DisponibilidadSlotToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DisponibilidadSlot&&(identical(other.horaInicio, horaInicio) || other.horaInicio == horaInicio)&&(identical(other.horaFin, horaFin) || other.horaFin == horaFin)&&(identical(other.estado, estado) || other.estado == estado));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,horaInicio,horaFin,estado);

@override
String toString() {
  return 'DisponibilidadSlot(horaInicio: $horaInicio, horaFin: $horaFin, estado: $estado)';
}


}

/// @nodoc
abstract mixin class _$DisponibilidadSlotCopyWith<$Res> implements $DisponibilidadSlotCopyWith<$Res> {
  factory _$DisponibilidadSlotCopyWith(_DisponibilidadSlot value, $Res Function(_DisponibilidadSlot) _then) = __$DisponibilidadSlotCopyWithImpl;
@override @useResult
$Res call({
 String horaInicio, String horaFin, EstadoSlot estado
});




}
/// @nodoc
class __$DisponibilidadSlotCopyWithImpl<$Res>
    implements _$DisponibilidadSlotCopyWith<$Res> {
  __$DisponibilidadSlotCopyWithImpl(this._self, this._then);

  final _DisponibilidadSlot _self;
  final $Res Function(_DisponibilidadSlot) _then;

/// Create a copy of DisponibilidadSlot
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? horaInicio = null,Object? horaFin = null,Object? estado = null,}) {
  return _then(_DisponibilidadSlot(
horaInicio: null == horaInicio ? _self.horaInicio : horaInicio // ignore: cast_nullable_to_non_nullable
as String,horaFin: null == horaFin ? _self.horaFin : horaFin // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as EstadoSlot,
  ));
}


}

// dart format on
